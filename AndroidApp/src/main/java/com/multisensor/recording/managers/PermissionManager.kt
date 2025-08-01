package com.multisensor.recording.managers

import android.app.Activity
import android.content.Context
import androidx.core.content.ContextCompat
import com.multisensor.recording.util.AllAndroidPermissions
import com.multisensor.recording.util.PermissionTool
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager class responsible for handling all permission-related logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 */
@Singleton
class PermissionManager @Inject constructor() {
    
    private var permissionRetryCount = 0
    private val maxPermissionRetries = 3
    
    /**
     * Interface for permission callbacks
     */
    interface PermissionCallback {
        fun onAllPermissionsGranted()
        fun onPermissionsTemporarilyDenied(deniedPermissions: List<String>, grantedCount: Int, totalCount: Int)
        fun onPermissionsPermanentlyDenied(deniedPermissions: List<String>)
    }
    
    /**
     * Check if all required permissions are granted
     */
    fun areAllPermissionsGranted(context: Context): Boolean {
        return AllAndroidPermissions.getDangerousPermissions().all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == android.content.pm.PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Request all required permissions using XXPermissions library
     */
    fun requestPermissions(activity: Activity, callback: PermissionCallback) {
        android.util.Log.d("PermissionManager", "[DEBUG_LOG] Requesting permissions, retry count: $permissionRetryCount")
        
        PermissionTool.requestAllDangerousPermissions(activity, object : PermissionTool.PermissionCallback {
            override fun onAllGranted() {
                android.util.Log.d("PermissionManager", "[DEBUG_LOG] All permissions granted")
                permissionRetryCount = 0
                callback.onAllPermissionsGranted()
            }
            
            override fun onTemporarilyDenied(deniedPermissions: List<String>) {
                val grantedCount = AllAndroidPermissions.getDangerousPermissions().size - deniedPermissions.size
                val totalCount = AllAndroidPermissions.getDangerousPermissions().size
                
                android.util.Log.d("PermissionManager", "[DEBUG_LOG] Permissions temporarily denied: ${deniedPermissions.joinToString(", ")}")
                android.util.Log.d("PermissionManager", "[DEBUG_LOG] Current retry count: $permissionRetryCount / $maxPermissionRetries")
                
                if (permissionRetryCount < maxPermissionRetries) {
                    permissionRetryCount++
                    android.util.Log.d("PermissionManager", "[DEBUG_LOG] Incrementing retry count to: $permissionRetryCount")
                    callback.onPermissionsTemporarilyDenied(deniedPermissions, grantedCount, totalCount)
                } else {
                    android.util.Log.d("PermissionManager", "[DEBUG_LOG] Max retries reached, treating as permanently denied")
                    callback.onPermissionsPermanentlyDenied(deniedPermissions)
                }
            }
            
            override fun onPermanentlyDeniedWithSettingsOpened(deniedPermissions: List<String>) {
                android.util.Log.d("PermissionManager", "[DEBUG_LOG] Permanently denied permissions, Settings opened: ${deniedPermissions.joinToString(", ")}")
                callback.onPermissionsPermanentlyDenied(deniedPermissions)
            }
            
            override fun onPermanentlyDeniedWithoutSettings(deniedPermissions: List<String>) {
                android.util.Log.d("PermissionManager", "[DEBUG_LOG] Permanently denied permissions, no Settings: ${deniedPermissions.joinToString(", ")}")
                callback.onPermissionsPermanentlyDenied(deniedPermissions)
            }
        })
    }
    
    /**
     * Get display name for a permission
     */
    fun getPermissionDisplayName(permission: String): String {
        return when {
            permission.contains("CAMERA") -> "Camera"
            permission.contains("RECORD_AUDIO") -> "Microphone"
            permission.contains("LOCATION") -> "Location"
            permission.contains("STORAGE") -> "Storage"
            permission.contains("NOTIFICATION") -> "Notifications"
            permission.contains("BLUETOOTH") -> "Bluetooth"
            else -> permission.substringAfterLast(".")
        }
    }
    
    /**
     * Reset permission retry counter
     */
    fun resetRetryCount() {
        permissionRetryCount = 0
        android.util.Log.d("PermissionManager", "[DEBUG_LOG] Permission retry counter reset to 0")
    }
    
    /**
     * Log current permission states for debugging
     */
    fun logCurrentPermissionStates(context: Context) {
        android.util.Log.d("PermissionManager", "[DEBUG_LOG] ===== CURRENT PERMISSION STATES =====")
        
        val allPermissions = AllAndroidPermissions.getDangerousPermissions()
        var grantedCount = 0
        var deniedCount = 0
        
        allPermissions.forEach { permission ->
            val isGranted = ContextCompat.checkSelfPermission(context, permission) == android.content.pm.PackageManager.PERMISSION_GRANTED
            val status = if (isGranted) "GRANTED" else "DENIED"
            if (isGranted) grantedCount++ else deniedCount++
            
            android.util.Log.d("PermissionManager", "[DEBUG_LOG] $permission: $status")
        }
        
        android.util.Log.d("PermissionManager", "[DEBUG_LOG] Summary: $grantedCount granted, $deniedCount denied out of ${allPermissions.size} total")
        android.util.Log.d("PermissionManager", "[DEBUG_LOG] ===== END PERMISSION STATES =====")
    }
    
    /**
     * Get all required permissions for formal analysis
     */
    fun getAllRequiredPermissions(): List<String> {
        return AllAndroidPermissions.getDangerousPermissions().toList()
    }
    
    /**
     * Get currently granted permissions for complexity analysis
     */
    fun getGrantedPermissions(context: Context): List<String> {
        return AllAndroidPermissions.getDangerousPermissions().filter { permission ->
            ContextCompat.checkSelfPermission(context, permission) == android.content.pm.PackageManager.PERMISSION_GRANTED
        }
    }
    
    /**
     * Get currently denied permissions for analysis
     */
    fun getDeniedPermissions(context: Context): List<String> {
        return AllAndroidPermissions.getDangerousPermissions().filter { permission ->
            ContextCompat.checkSelfPermission(context, permission) != android.content.pm.PackageManager.PERMISSION_GRANTED
        }
    }
}