package com.multisensor.recording.util

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.hjq.permissions.OnPermissionCallback
import com.hjq.permissions.Permission
import com.hjq.permissions.XXPermissions

/**
 * Enhanced permission handling utility using XXPermissions library.
 * Provides superior permanent denial detection and recovery compared to standard Android API.
 *
 * Based on IRCamera implementation with improvements for permanently denied permissions.
 */
object PermissionTool {
    /**
     * Request all dangerous permissions required by the app
     * Uses three-phase approach to handle XXPermissions library restriction and Android sequential location requirements:
     * Phase 1: Non-location permissions
     * Phase 2: Foreground location permissions (ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION)
     * Phase 3: Background location permissions (ACCESS_BACKGROUND_LOCATION) - only after foreground is granted
     */
    fun requestAllDangerousPermissions(
        context: Context,
        callback: PermissionCallback,
    ) {
        // Start with non-location permissions first to avoid XXPermissions library restriction
        val nonLocationPermissions = getNonLocationDangerousPermissions()
        if (nonLocationPermissions.isNotEmpty()) {
            requestPermissions(
                context,
                nonLocationPermissions,
                "App Permissions",
                ThreePhasePermissionCallback(context, callback),
            )
        } else {
            // No non-location permissions, go directly to foreground location permissions
            val foregroundLocationPermissions = getForegroundLocationPermissions()
            if (foregroundLocationPermissions.isNotEmpty()) {
                requestPermissions(
                    context,
                    foregroundLocationPermissions,
                    "Foreground Location Permissions",
                    ThreePhasePermissionCallback(context, callback, startFromPhase2 = true),
                )
            } else {
                // No foreground location permissions, go directly to background location
                val backgroundLocationPermissions = getBackgroundLocationPermissions()
                if (backgroundLocationPermissions.isNotEmpty()) {
                    requestPermissions(context, backgroundLocationPermissions, "Background Location Permissions", callback)
                } else {
                    // No permissions needed at all
                    callback.onAllGranted()
                }
            }
        }
    }

    /**
     * Request camera permission
     */
    fun requestCamera(
        context: Context,
        callback: PermissionCallback,
    ) {
        requestPermissions(context, listOf(Permission.CAMERA), "Camera", callback)
    }

    /**
     * Request microphone permission
     */
    fun requestMicrophone(
        context: Context,
        callback: PermissionCallback,
    ) {
        requestPermissions(context, listOf(Permission.RECORD_AUDIO), "Microphone", callback)
    }

    /**
     * Request location permissions
     */
    fun requestLocation(
        context: Context,
        callback: PermissionCallback,
    ) {
        val permissions = listOf(Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION)
        requestPermissions(context, permissions, "Location", callback)
    }

    /**
     * Request storage permissions (handles different Android versions)
     */
    fun requestStorage(
        context: Context,
        callback: PermissionCallback,
    ) {
        val permissions = getStoragePermissions()
        requestPermissions(context, permissions, "Storage", callback)
    }

    /**
     * Check if all dangerous permissions are granted
     */
    fun areAllDangerousPermissionsGranted(context: Context): Boolean = XXPermissions.isGranted(context, getAllDangerousPermissions())

    /**
     * Get list of missing dangerous permissions
     */
    fun getMissingDangerousPermissions(context: Context): List<String> {
        val allPermissions = getAllDangerousPermissions()
        return allPermissions.filter { !XXPermissions.isGranted(context, it) }
    }

    private fun requestPermissions(
        context: Context,
        permissions: List<String>,
        permissionType: String,
        callback: PermissionCallback,
    ) {
        // Safety check: Ensure background location is never mixed with other permissions
        // This prevents XXPermissions library restriction errors
        val hasBackgroundLocation = permissions.contains(Permission.ACCESS_BACKGROUND_LOCATION)
        val hasOtherPermissions = permissions.any { it != Permission.ACCESS_BACKGROUND_LOCATION }
        
        if (hasBackgroundLocation && hasOtherPermissions) {
            android.util.Log.e("PermissionTool", "[ERROR] Background location cannot be requested with other permissions. Separating requests.")
            
            // Request non-background-location permissions first
            val nonBackgroundPermissions = permissions.filter { it != Permission.ACCESS_BACKGROUND_LOCATION }
            val backgroundPermissions = listOf(Permission.ACCESS_BACKGROUND_LOCATION)
            
            // Create a chained callback to request background location after other permissions
            requestPermissions(context, nonBackgroundPermissions, permissionType, object : PermissionCallback {
                override fun onAllGranted() {
                    // Now request background location separately
                    requestPermissions(context, backgroundPermissions, "Background Location", callback)
                }
                
                override fun onTemporarilyDenied(deniedPermissions: List<String>) {
                    callback.onTemporarilyDenied(deniedPermissions)
                }
                
                override fun onPermanentlyDeniedWithSettingsOpened(deniedPermissions: List<String>) {
                    callback.onPermanentlyDeniedWithSettingsOpened(deniedPermissions)
                }
                
                override fun onPermanentlyDeniedWithoutSettings(deniedPermissions: List<String>) {
                    callback.onPermanentlyDeniedWithoutSettings(deniedPermissions)
                }
            })
            return
        }
        
        XXPermissions
            .with(context)
            .permission(permissions)
            .request(
                object : OnPermissionCallback {
                    override fun onGranted(
                        permissions: MutableList<String>,
                        allGranted: Boolean,
                    ) {
                        if (allGranted) {
                            callback.onAllGranted()
                        } else {
                            callback.onPartiallyGranted(permissions.toList())
                        }
                    }

                    override fun onDenied(
                        permissions: MutableList<String>,
                        never: Boolean,
                    ) {
                        if (never) {
                            // Permanently denied - show dialog with Settings navigation
                            showPermanentDenialDialog(context, permissions.toList(), permissionType, callback)
                        } else {
                            // Temporarily denied - can be requested again
                            callback.onTemporarilyDenied(permissions.toList())
                        }
                    }
                },
            )
    }

    private fun showPermanentDenialDialog(
        context: Context,
        deniedPermissions: List<String>,
        permissionType: String,
        callback: PermissionCallback,
    ) {
        val permissionNames = deniedPermissions.map { getPermissionDisplayName(it) }
        val message =
            buildString {
                append("$permissionType permissions have been permanently denied.\n\n")
                append("To use this app properly, please enable the following permissions in Settings:\n\n")
                permissionNames.forEach { name ->
                    append("• $name\n")
                }
                append("\nWould you like to open Settings now?")
            }

        AlertDialog
            .Builder(context)
            .setTitle("Permissions Required")
            .setMessage(message)
            .setPositiveButton("Open Settings") { _, _ ->
                openAppSettings(context)
                callback.onPermanentlyDeniedWithSettingsOpened(deniedPermissions)
            }.setNegativeButton("Cancel") { _, _ ->
                callback.onPermanentlyDeniedWithoutSettings(deniedPermissions)
            }.setCancelable(false)
            .show()
    }

    private fun openAppSettings(context: Context) {
        try {
            // Try using XXPermissions built-in method first
            XXPermissions.startPermissionActivity(context, emptyList())
        } catch (e: Exception) {
            // Fallback to manual Settings intent
            try {
                val intent =
                    Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                        data = Uri.fromParts("package", context.packageName, null)
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                context.startActivity(intent)
            } catch (e2: Exception) {
                // Final fallback - show toast with instructions
                Toast
                    .makeText(
                        context,
                        "Please go to Settings > Apps > ${context.applicationInfo.loadLabel(
                            context.packageManager,
                        )} > Permissions to enable required permissions",
                        Toast.LENGTH_LONG,
                    ).show()
            }
        }
    }

    private fun getAllDangerousPermissions(): List<String> {
        val permissions = mutableListOf<String>()
        permissions.addAll(getNonLocationDangerousPermissions())
        permissions.addAll(getForegroundLocationPermissions())
        // Note: Background location permissions are excluded to prevent XXPermissions library restriction
        // They are handled separately through the three-phase permission system
        
        // Safety check: Remove any background location permissions that might have been included
        return permissions.filter { it != Permission.ACCESS_BACKGROUND_LOCATION }
    }

    /**
     * Get all non-location dangerous permissions required for sensor recording app
     * These can be requested together without XXPermissions restrictions
     */
    private fun getNonLocationDangerousPermissions(): List<String> {
        val permissions = mutableListOf<String>()

        // Storage (version-dependent)
        permissions.addAll(getStoragePermissions())

        // Camera and Audio - essential for sensor recording
        permissions.addAll(
            listOf(
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
            ),
        )

        // Notifications (Android 13+) - needed for foreground service notifications
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Permission.POST_NOTIFICATIONS)
        }

        // Safety check: Ensure no location permissions are included
        return permissions.filter { permission ->
            permission != Permission.ACCESS_FINE_LOCATION &&
            permission != Permission.ACCESS_COARSE_LOCATION &&
            permission != Permission.ACCESS_BACKGROUND_LOCATION
        }
    }

    /**
     * Get foreground location permissions only
     * These must be granted before background location can be requested
     */
    private fun getForegroundLocationPermissions(): List<String> =
        listOf(
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
        )

    /**
     * Get background location permission only
     * This can only be requested after foreground location is granted
     */
    private fun getBackgroundLocationPermissions(): List<String> =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            listOf(Permission.ACCESS_BACKGROUND_LOCATION)
        } else {
            emptyList()
        }

    /**
     * Get all location permissions (for compatibility)
     * Note: These should be requested sequentially, not together
     */
    private fun getLocationPermissions(): List<String> {
        val permissions = mutableListOf<String>()
        permissions.addAll(getForegroundLocationPermissions())
        permissions.addAll(getBackgroundLocationPermissions())
        return permissions
    }

    private fun getStoragePermissions(): List<String> =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Android 13+ - Use granular media permissions
            listOf(
                Permission.READ_MEDIA_IMAGES,
                Permission.READ_MEDIA_VIDEO,
                Permission.READ_MEDIA_AUDIO,
            )
        } else {
            // Android 12 and below - Use legacy storage permissions
            listOf(
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            )
        }

    private fun getPermissionDisplayName(permission: String): String =
        when (permission) {
            Permission.CAMERA -> "Camera"
            Permission.RECORD_AUDIO -> "Microphone"
            Permission.ACCESS_FINE_LOCATION -> "Fine Location"
            Permission.ACCESS_COARSE_LOCATION -> "Coarse Location"
            Permission.ACCESS_BACKGROUND_LOCATION -> "Background Location"
            Permission.READ_EXTERNAL_STORAGE -> "Read Storage"
            Permission.WRITE_EXTERNAL_STORAGE -> "Write Storage"
            Permission.READ_MEDIA_IMAGES -> "Read Images"
            Permission.READ_MEDIA_VIDEO -> "Read Videos"
            Permission.READ_MEDIA_AUDIO -> "Read Audio"
            Permission.POST_NOTIFICATIONS -> "Notifications"
            else -> permission.substringAfterLast(".")
        }

    /**
     * Three-phase permission callback that handles XXPermissions library restriction and Android sequential location requirements
     * Phase 1: Non-location permissions
     * Phase 2: Foreground location permissions (ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION)
     * Phase 3: Background location permissions (ACCESS_BACKGROUND_LOCATION) - only after foreground is granted
     */
    private class ThreePhasePermissionCallback(
        private val context: Context,
        private val originalCallback: PermissionCallback,
        private val startFromPhase2: Boolean = false,
    ) : PermissionCallback {
        private var phase1Completed = startFromPhase2
        private var phase2Completed = false
        private val phase1DeniedPermissions = mutableListOf<String>()
        private val phase2DeniedPermissions = mutableListOf<String>()
        private val phase3DeniedPermissions = mutableListOf<String>()

        override fun onAllGranted() {
            when {
                !phase1Completed -> {
                    // Phase 1 (non-location) completed successfully, start Phase 2 (foreground location)
                    phase1Completed = true
                    val foregroundLocationPermissions = getForegroundLocationPermissions()
                    if (foregroundLocationPermissions.isNotEmpty()) {
                        requestPermissions(context, foregroundLocationPermissions, "Foreground Location Permissions", this)
                    } else {
                        // No foreground location permissions needed, check background location
                        checkBackgroundLocationPermissions()
                    }
                }
                !phase2Completed -> {
                    // Phase 2 (foreground location) completed successfully, start Phase 3 (background location)
                    phase2Completed = true
                    val backgroundLocationPermissions = getBackgroundLocationPermissions()
                    if (backgroundLocationPermissions.isNotEmpty()) {
                        requestPermissions(context, backgroundLocationPermissions, "Background Location Permissions", this)
                    } else {
                        // No background location permissions needed, I'm done
                        originalCallback.onAllGranted()
                    }
                }
                else -> {
                    // Phase 3 (background location) completed successfully, all permissions granted
                    originalCallback.onAllGranted()
                }
            }
        }

        override fun onTemporarilyDenied(deniedPermissions: List<String>) {
            when {
                !phase1Completed -> {
                    // Phase 1 denied permissions
                    phase1DeniedPermissions.addAll(deniedPermissions)
                    phase1Completed = true

                    // Continue to Phase 2 even if Phase 1 had denials
                    val foregroundLocationPermissions = getForegroundLocationPermissions()
                    if (foregroundLocationPermissions.isNotEmpty()) {
                        requestPermissions(context, foregroundLocationPermissions, "Foreground Location Permissions", this)
                    } else {
                        checkBackgroundLocationPermissions()
                    }
                }
                !phase2Completed -> {
                    // Phase 2 (foreground location) denied permissions
                    phase2DeniedPermissions.addAll(deniedPermissions)
                    phase2Completed = true

                    // CRITICAL: Do NOT request background location if foreground location is denied
                    // This breaks the retry loop by not requesting background location without foreground location
                    android.util.Log.d("PermissionTool", "[DEBUG_LOG] Foreground location denied, skipping background location request")

                    // Report all denied permissions from all phases
                    val allDeniedPermissions = phase1DeniedPermissions + phase2DeniedPermissions
                    if (allDeniedPermissions.isNotEmpty()) {
                        originalCallback.onTemporarilyDenied(allDeniedPermissions)
                    } else {
                        originalCallback.onAllGranted()
                    }
                }
                else -> {
                    // Phase 3 (background location) denied permissions
                    phase3DeniedPermissions.addAll(deniedPermissions)

                    // Combine all denied permissions from all phases
                    val allDeniedPermissions = phase1DeniedPermissions + phase2DeniedPermissions + phase3DeniedPermissions
                    if (allDeniedPermissions.isNotEmpty()) {
                        originalCallback.onTemporarilyDenied(allDeniedPermissions)
                    } else {
                        originalCallback.onAllGranted()
                    }
                }
            }
        }

        override fun onPermanentlyDeniedWithSettingsOpened(deniedPermissions: List<String>) {
            when {
                !phase1Completed -> {
                    phase1DeniedPermissions.addAll(deniedPermissions)
                    phase1Completed = true

                    // Continue to Phase 2 even if Phase 1 had permanent denials
                    val foregroundLocationPermissions = getForegroundLocationPermissions()
                    if (foregroundLocationPermissions.isNotEmpty()) {
                        requestPermissions(context, foregroundLocationPermissions, "Foreground Location Permissions", this)
                    } else {
                        checkBackgroundLocationPermissions()
                    }
                }
                !phase2Completed -> {
                    phase2DeniedPermissions.addAll(deniedPermissions)
                    phase2Completed = true

                    // Do NOT request background location if foreground location is permanently denied
                    val allDeniedPermissions = phase1DeniedPermissions + phase2DeniedPermissions
                    originalCallback.onPermanentlyDeniedWithSettingsOpened(allDeniedPermissions)
                }
                else -> {
                    phase3DeniedPermissions.addAll(deniedPermissions)
                    val allDeniedPermissions = phase1DeniedPermissions + phase2DeniedPermissions + phase3DeniedPermissions
                    originalCallback.onPermanentlyDeniedWithSettingsOpened(allDeniedPermissions)
                }
            }
        }

        override fun onPermanentlyDeniedWithoutSettings(deniedPermissions: List<String>) {
            when {
                !phase1Completed -> {
                    phase1DeniedPermissions.addAll(deniedPermissions)
                    phase1Completed = true

                    // Continue to Phase 2 even if Phase 1 had permanent denials
                    val foregroundLocationPermissions = getForegroundLocationPermissions()
                    if (foregroundLocationPermissions.isNotEmpty()) {
                        requestPermissions(context, foregroundLocationPermissions, "Foreground Location Permissions", this)
                    } else {
                        checkBackgroundLocationPermissions()
                    }
                }
                !phase2Completed -> {
                    phase2DeniedPermissions.addAll(deniedPermissions)
                    phase2Completed = true

                    // Do NOT request background location if foreground location is permanently denied
                    val allDeniedPermissions = phase1DeniedPermissions + phase2DeniedPermissions
                    originalCallback.onPermanentlyDeniedWithoutSettings(allDeniedPermissions)
                }
                else -> {
                    phase3DeniedPermissions.addAll(deniedPermissions)
                    val allDeniedPermissions = phase1DeniedPermissions + phase2DeniedPermissions + phase3DeniedPermissions
                    originalCallback.onPermanentlyDeniedWithoutSettings(allDeniedPermissions)
                }
            }
        }

        private fun checkBackgroundLocationPermissions() {
            val backgroundLocationPermissions = getBackgroundLocationPermissions()
            if (backgroundLocationPermissions.isNotEmpty()) {
                requestPermissions(context, backgroundLocationPermissions, "Background Location Permissions", this)
            } else {
                // No background location permissions needed, report any denied permissions
                val allDeniedPermissions = phase1DeniedPermissions + phase2DeniedPermissions
                if (allDeniedPermissions.isNotEmpty()) {
                    originalCallback.onTemporarilyDenied(allDeniedPermissions)
                } else {
                    originalCallback.onAllGranted()
                }
            }
        }
    }

    /**
     * Callback interface for permission requests
     */
    interface PermissionCallback {
        /**
         * Called when all requested permissions are granted
         */
        fun onAllGranted()

        /**
         * Called when some permissions are granted but not all
         */
        fun onPartiallyGranted(grantedPermissions: List<String>) {
            // Default implementation - treat as failure
            onTemporarilyDenied(emptyList())
        }

        /**
         * Called when permissions are denied but can still be requested again
         */
        fun onTemporarilyDenied(deniedPermissions: List<String>)

        /**
         * Called when permissions are permanently denied and Settings was opened
         */
        fun onPermanentlyDeniedWithSettingsOpened(deniedPermissions: List<String>) {
            // Default implementation
            onPermanentlyDeniedWithoutSettings(deniedPermissions)
        }

        /**
         * Called when permissions are permanently denied but user chose not to open Settings
         */
        fun onPermanentlyDeniedWithoutSettings(deniedPermissions: List<String>)
    }
}
