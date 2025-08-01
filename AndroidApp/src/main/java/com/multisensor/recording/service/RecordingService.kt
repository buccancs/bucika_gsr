package com.multisensor.recording.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.multisensor.recording.MainActivity
import com.multisensor.recording.R
import com.multisensor.recording.network.CommandProcessor
import com.multisensor.recording.network.JsonSocketClient
import com.multisensor.recording.network.NetworkConfiguration
import com.multisensor.recording.network.NetworkQualityMonitor
import com.multisensor.recording.recording.AdaptiveFrameRateController
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.streaming.PreviewStreamer
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Foreground service responsible for managing multi-sensor recording sessions.
 * This service ensures recording continues even when the app is in the background
 * and provides a persistent notification to the user.
 */
@AndroidEntryPoint
class RecordingService : Service() {
    @Inject
    lateinit var cameraRecorder: CameraRecorder

    @Inject
    lateinit var thermalRecorder: ThermalRecorder

    @Inject
    lateinit var shimmerRecorder: ShimmerRecorder

    @Inject
    lateinit var sessionManager: SessionManager


    @Inject
    lateinit var jsonSocketClient: JsonSocketClient

    @Inject
    lateinit var commandProcessor: CommandProcessor

    @Inject
    lateinit var previewStreamer: PreviewStreamer

    @Inject
    lateinit var networkConfiguration: NetworkConfiguration

    @Inject
    lateinit var networkQualityMonitor: NetworkQualityMonitor

    @Inject
    lateinit var adaptiveFrameRateController: AdaptiveFrameRateController

    @Inject
    lateinit var logger: Logger

    private val serviceScope = CoroutineScope(Dispatchers.Default + Job())
    private var isRecording = false
    private var currentSessionId: String? = null

    companion object {
        const val ACTION_START_RECORDING = "com.multisensor.recording.START_RECORDING"
        const val ACTION_STOP_RECORDING = "com.multisensor.recording.STOP_RECORDING"
        const val ACTION_GET_STATUS = "com.multisensor.recording.GET_STATUS"

        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "recording_channel"
        private const val CHANNEL_NAME = "Recording Service"
    }

    /**
     * Data class representing comprehensive device status information
     */
    data class DeviceStatusInfo(
        val isRecording: Boolean,
        val currentSessionId: String?,
        val recordingStartTime: Long?,
        val cameraStatus: String,
        val thermalStatus: String,
        val shimmerStatus: String,
        val batteryLevel: Int?,
        val availableStorage: String?,
        val deviceTemperature: Double?,
        val networkConfig: String,
        val connectionStatus: String,
        val previewStreamingActive: Boolean,
        val timestamp: Long,
        val deviceModel: String,
        val androidVersion: String,
    ) {
        companion object {
            fun createErrorStatus(errorMessage: String): DeviceStatusInfo =
                DeviceStatusInfo(
                    isRecording = false,
                    currentSessionId = null,
                    recordingStartTime = null,
                    cameraStatus = "error",
                    thermalStatus = "error",
                    shimmerStatus = "error",
                    batteryLevel = null,
                    availableStorage = null,
                    deviceTemperature = null,
                    networkConfig = "error: $errorMessage",
                    connectionStatus = "error",
                    previewStreamingActive = false,
                    timestamp = System.currentTimeMillis(),
                    deviceModel = android.os.Build.MODEL,
                    androidVersion = android.os.Build.VERSION.RELEASE,
                )
        }
    }

    override fun onCreate() {
        super.onCreate()
        logger.info("RecordingService created")
        createNotificationChannel()


        // Initialize JSON Socket Client and Command Processor
        initializeJsonCommunication()

        // Inject PreviewStreamer into CameraRecorder (method injection for scoping compatibility)
        cameraRecorder.setPreviewStreamer(previewStreamer)

        // Initialize Adaptive Frame Rate Control
        initializeAdaptiveFrameRateControl()

        logger.info("RecordingService initialization complete")
    }

    /**
     * Initialize adaptive frame rate control system for 
     */
    private fun initializeAdaptiveFrameRateControl() {
        try {
            logger.info("[DEBUG_LOG] Initializing adaptive frame rate control system")

            // Get network configuration for monitoring
            val serverConfig = networkConfiguration.getServerConfiguration()

            // Start network quality monitoring
            networkQualityMonitor.startMonitoring(serverConfig.serverIp, serverConfig.legacyPort)

            // Set up adaptive frame rate controller with PreviewStreamer integration
            adaptiveFrameRateController.addListener(
                object : AdaptiveFrameRateController.FrameRateChangeListener {
                    override fun onFrameRateChanged(
                        newFrameRate: Float,
                        reason: String,
                    ) {
                        logger.info("[DEBUG_LOG] Adaptive frame rate changed to ${newFrameRate}fps - $reason")
                        previewStreamer.updateFrameRate(newFrameRate)
                    }

                    override fun onAdaptationModeChanged(isAdaptive: Boolean) {
                        logger.info("[DEBUG_LOG] Adaptive mode changed: $isAdaptive")
                    }
                },
            )

            // Start the adaptive frame rate controller
            adaptiveFrameRateController.start()

            logger.info("[DEBUG_LOG] Adaptive frame rate control system initialized successfully")
        } catch (e: Exception) {
            logger.error("Failed to initialize adaptive frame rate control system", e)
        }
    }

    /**
     * Initialize JSON-based communication system for 
     */
    private fun initializeJsonCommunication() {
        try {
            // Connect CommandProcessor to JsonSocketClient
            commandProcessor.setSocketClient(jsonSocketClient)

            // Set command callback for JsonSocketClient
            jsonSocketClient.setCommandCallback { message ->
                commandProcessor.processCommand(message)
            }

            // Configure and start JSON socket connection using NetworkConfiguration
            val serverConfig = networkConfiguration.getServerConfiguration()
            jsonSocketClient.configure(serverConfig.serverIp, serverConfig.jsonPort)
            jsonSocketClient.connect()

            logger.info("JSON communication system initialized successfully: ${serverConfig.getJsonAddress()}")
            logger.info("Network configuration: ${networkConfiguration.getConfigurationSummary()}")
        } catch (e: Exception) {
            logger.error("Failed to initialize JSON communication system", e)
        }
    }

    override fun onStartCommand(
        intent: Intent?,
        flags: Int,
        startId: Int,
    ): Int {
        when (intent?.action) {
            ACTION_START_RECORDING -> {
                startRecording()
            }
            ACTION_STOP_RECORDING -> {
                stopRecording()
            }
            ACTION_GET_STATUS -> {
                broadcastCurrentStatus()
            }
        }

        return START_STICKY // Restart service if killed by system
    }

    override fun onBind(intent: Intent?): IBinder? {
        // This service doesn't support binding
        return null
    }

    override fun onDestroy() {
        super.onDestroy()
        logger.info("RecordingService destroyed")

        // Ensure recording is stopped
        if (isRecording) {
            serviceScope.launch {
                stopRecordingInternal()
            }
        }

        // Stop preview streaming
        previewStreamer.stopStreaming()

        // Stop adaptive frame rate control system ()
        try {
            adaptiveFrameRateController.stop()
            networkQualityMonitor.stopMonitoring()
            logger.info("[DEBUG_LOG] Adaptive frame rate control system stopped")
        } catch (e: Exception) {
            logger.error("Error stopping adaptive frame rate control system", e)
        }


        // Stop JSON socket connection (port 9000)
        jsonSocketClient.disconnect()

        // Cancel all coroutines
        serviceScope.cancel()

        logger.info("RecordingService cleanup complete")
    }

    /**
     * Broadcast current recording status to all connected clients
     */
    private fun broadcastCurrentStatus() {
        serviceScope.launch {
            try {
                logger.info("Broadcasting current status - Recording: $isRecording, Session: $currentSessionId")

                // Gather comprehensive status information
                val statusInfo = gatherStatusInformation()


                // Broadcast via JSON socket connection ()
                broadcastStatusViaJsonSocket(statusInfo)

                // Send local broadcast for UI updates
                sendLocalStatusBroadcast(statusInfo)

                logger.info("Status broadcast completed successfully")
            } catch (e: Exception) {
                logger.error("Failed to broadcast current status", e)
            }
        }
    }

    /**
     * Gather comprehensive status information
     */
    private suspend fun gatherStatusInformation(): DeviceStatusInfo =
        try {
            DeviceStatusInfo(
                isRecording = isRecording,
                currentSessionId = currentSessionId,
                recordingStartTime = if (isRecording) System.currentTimeMillis() else null,
                // Camera status
                cameraStatus = getCameraStatus(),
                thermalStatus = getThermalStatus(),
                shimmerStatus = getShimmerStatus(),
                // Device information
                batteryLevel = getBatteryLevel(),
                availableStorage = getAvailableStorage(),
                deviceTemperature = getDeviceTemperature(),
                // Network status
                networkConfig = networkConfiguration.getConfigurationSummary(),
                connectionStatus = getConnectionStatus(),
                // Preview streaming status
                previewStreamingActive = previewStreamer.getStreamingStats().isStreaming,
                // System information
                timestamp = System.currentTimeMillis(),
                deviceModel = android.os.Build.MODEL,
                androidVersion = android.os.Build.VERSION.RELEASE,
            )
        } catch (e: Exception) {
            logger.error("Error gathering status information", e)
            DeviceStatusInfo.createErrorStatus(e.message ?: "Unknown error")
        }


    /**
     * Broadcast status via JSON socket connection
     */
    private fun broadcastStatusViaJsonSocket(statusInfo: DeviceStatusInfo) {
        try {
            // Send status update via JSON socket client
            jsonSocketClient.sendStatusUpdate(
                battery = statusInfo.batteryLevel,
                storage = statusInfo.availableStorage,
                temperature = statusInfo.deviceTemperature,
                recording = statusInfo.isRecording,
            )

            logger.debug("JSON status broadcast sent successfully")
        } catch (e: Exception) {
            logger.error("Failed to broadcast status via JSON socket", e)
        }
    }

    /**
     * Send local broadcast for UI updates
     */
    private fun sendLocalStatusBroadcast(statusInfo: DeviceStatusInfo) {
        try {
            val intent =
                Intent("com.multisensor.recording.STATUS_UPDATE").apply {
                    putExtra("is_recording", statusInfo.isRecording)
                    putExtra("session_id", statusInfo.currentSessionId)
                    putExtra("battery_level", statusInfo.batteryLevel)
                    putExtra("available_storage", statusInfo.availableStorage)
                    putExtra("preview_streaming", statusInfo.previewStreamingActive)
                    putExtra("timestamp", statusInfo.timestamp)
                }

            sendBroadcast(intent)
            logger.debug("Local status broadcast sent")
        } catch (e: Exception) {
            logger.error("Failed to send local status broadcast", e)
        }
    }


    /**
     * Get camera recording status
     */
    private fun getCameraStatus(): String =
        try {
            if (isRecording) "recording" else "ready"
        } catch (e: Exception) {
            "error"
        }

    /**
     * Get thermal camera status
     */
    private fun getThermalStatus(): String =
        try {
            val status = thermalRecorder.getThermalCameraStatus()
            if (status.isRecording) {
                "recording"
            } else if (status.isAvailable) {
                "ready"
            } else {
                "unavailable"
            }
        } catch (e: Exception) {
            "error"
        }

    /**
     * Get Shimmer sensor status
     */
    private fun getShimmerStatus(): String =
        try {
            // Get actual Shimmer status from ShimmerRecorder
            val status = shimmerRecorder.getShimmerStatus()
            when {
                !status.isAvailable -> "unavailable"
                !status.isConnected -> "disconnected"
                status.isRecording -> "recording"
                status.isConnected -> "ready"
                else -> "unknown"
            }
        } catch (e: Exception) {
            "error"
        }

    /**
     * Get device battery level
     */
    private fun getBatteryLevel(): Int? =
        try {
            val batteryManager = getSystemService(Context.BATTERY_SERVICE) as android.os.BatteryManager
            batteryManager.getIntProperty(android.os.BatteryManager.BATTERY_PROPERTY_CAPACITY)
        } catch (e: Exception) {
            null
        }

    /**
     * Get available storage space
     */
    private fun getAvailableStorage(): String? =
        try {
            val externalDir = getExternalFilesDir(null)
            if (externalDir != null) {
                val stat = android.os.StatFs(externalDir.path)
                val availableBytes = stat.availableBytes
                val availableGB = availableBytes / (1024 * 1024 * 1024)
                "${availableGB}GB"
            } else {
                null
            }
        } catch (e: Exception) {
            null
        }

    /**
     * Get device temperature (if available)
     */
    private fun getDeviceTemperature(): Double? =
        try {
            // Android doesn't provide easy access to device temperature
            // This would require thermal management APIs or hardware-specific implementations
            null
        } catch (e: Exception) {
            null
        }

    /**
     * Get network connection status
     */
    private fun getConnectionStatus(): String =
        try {
            val jsonConnected = jsonSocketClient.isConnected()
            if (jsonConnected) "connected" else "disconnected"
        } catch (e: Exception) {
            "error"
        }


    private fun startRecording() {
        if (isRecording) {
            logger.warning("Recording already in progress")
            return
        }

        serviceScope.launch {
            try {
                logger.info("Starting recording session...")

                // Create new session
                currentSessionId = sessionManager.createNewSession()
                logger.info("Created session: $currentSessionId")

                // Start foreground service with notification
                startForeground(NOTIFICATION_ID, createRecordingNotification())

                // Initialize and start all recorders
                val cameraSessionInfo = cameraRecorder.startSession(recordVideo = true, captureRaw = false)
                val thermalStarted = thermalRecorder.startRecording(currentSessionId!!)
                val shimmerStarted = shimmerRecorder.startRecording(currentSessionId!!)

                if (cameraSessionInfo != null) {
                    isRecording = true

                    // Start preview streaming
                    previewStreamer.startStreaming()

                    logger.info("Recording started successfully")
                    updateNotification("Recording in progress - Session: $currentSessionId")
                } else {
                    logger.error("Failed to start camera recording")
                    stopRecordingInternal()
                }

                logger.info("Recording status - Camera: ${cameraSessionInfo != null}, Thermal: $thermalStarted, Shimmer: $shimmerStarted")
            } catch (e: Exception) {
                logger.error("Error starting recording", e)
                stopRecordingInternal()
            }
        }
    }

    private fun stopRecording() {
        if (!isRecording) {
            logger.warning("No recording in progress")
            return
        }

        serviceScope.launch {
            stopRecordingInternal()
        }
    }

    private suspend fun stopRecordingInternal() {
        try {
            logger.info("Stopping recording session...")

            // Stop all recorders
            cameraRecorder.stopSession()
            thermalRecorder.stopRecording()
            shimmerRecorder.stopRecording()

            // Stop preview streaming
            previewStreamer.stopStreaming()

            // Finalize session
            currentSessionId?.let { sessionId ->
                sessionManager.finalizeCurrentSession()
                logger.info("Session finalized: $sessionId")
            }

            isRecording = false
            currentSessionId = null

            // Update notification
            updateNotification("Recording stopped")

            // Stop foreground service after a delay to show final notification
            kotlinx.coroutines.delay(2000)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                stopForeground(STOP_FOREGROUND_REMOVE)
            } else {
                @Suppress("DEPRECATION")
                stopForeground(true)
            }
            stopSelf()

            logger.info("Recording stopped successfully")
        } catch (e: Exception) {
            logger.error("Error stopping recording", e)
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel =
                NotificationChannel(
                    CHANNEL_ID,
                    CHANNEL_NAME,
                    NotificationManager.IMPORTANCE_LOW,
                ).apply {
                    description = "Notifications for multi-sensor recording sessions"
                    setShowBadge(false)
                }

            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createRecordingNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent =
            PendingIntent.getActivity(
                this,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )

        return NotificationCompat
            .Builder(this, CHANNEL_ID)
            .setContentTitle("Multi-Sensor Recording")
            .setContentText("Preparing to record...")
            .setSmallIcon(R.drawable.ic_multisensor_idle)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun updateNotification(message: String) {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent =
            PendingIntent.getActivity(
                this,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )

        val notification =
            NotificationCompat
                .Builder(this, CHANNEL_ID)
                .setContentTitle("Multi-Sensor Recording")
                .setContentText(message)
                .setSmallIcon(if (isRecording) R.drawable.ic_multisensor_recording else R.drawable.ic_multisensor_idle)
                .setContentIntent(pendingIntent)
                .setOngoing(isRecording)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build()

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID, notification)
    }
}
