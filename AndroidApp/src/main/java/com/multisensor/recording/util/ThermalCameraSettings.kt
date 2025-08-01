package com.multisensor.recording.util

import android.content.Context
import android.content.SharedPreferences
import androidx.preference.PreferenceManager
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * ThermalCameraSettings manages thermal camera configuration and preferences.
 * Provides centralized access to thermal camera settings and ensures they are
 * applied consistently during recording sessions.
 */
@Singleton
class ThermalCameraSettings
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
    ) {
        private val prefs: SharedPreferences = PreferenceManager.getDefaultSharedPreferences(context)

        companion object {
            // Preference keys
            private const val KEY_THERMAL_ENABLED = "enable_thermal_recording"
            private const val KEY_THERMAL_FRAME_RATE = "thermal_frame_rate"
            private const val KEY_THERMAL_COLOR_PALETTE = "thermal_color_palette"
            private const val KEY_THERMAL_TEMP_RANGE = "thermal_temperature_range"
            private const val KEY_THERMAL_EMISSIVITY = "thermal_emissivity"
            private const val KEY_THERMAL_AUTO_CALIBRATION = "thermal_auto_calibration"
            private const val KEY_THERMAL_HIGH_RESOLUTION = "thermal_high_resolution"
            private const val KEY_THERMAL_TEMP_UNITS = "thermal_temperature_units"
            private const val KEY_THERMAL_USB_PRIORITY = "thermal_usb_priority"
            private const val KEY_THERMAL_DATA_FORMAT = "thermal_data_format"

            // Default values
            private const val DEFAULT_FRAME_RATE = 25
            private const val DEFAULT_COLOR_PALETTE = "iron"
            private const val DEFAULT_TEMP_RANGE = "auto"
            private const val DEFAULT_EMISSIVITY = 0.95f
            private const val DEFAULT_TEMP_UNITS = "celsius"
            private const val DEFAULT_DATA_FORMAT = "radiometric"
        }

        /**
         * Data class representing thermal camera configuration
         */
        data class ThermalConfig(
            val isEnabled: Boolean,
            val frameRate: Int,
            val colorPalette: String,
            val temperatureRange: String,
            val emissivity: Float,
            val autoCalibration: Boolean,
            val highResolution: Boolean,
            val temperatureUnits: String,
            val usbPriority: Boolean,
            val dataFormat: String,
        ) {
            /**
             * Get display name for temperature range
             */
            fun getTemperatureRangeDisplay(): String =
                when (temperatureRange) {
                    "auto" -> "Auto Range"
                    "-20_150" -> "-20°C to 150°C"
                    "0_100" -> "0°C to 100°C"
                    "15_45" -> "15°C to 45°C (Human Body)"
                    "20_40" -> "20°C to 40°C (Room Temp)"
                    "custom" -> "Custom Range"
                    else -> temperatureRange
                }

            /**
             * Get display name for color palette
             */
            fun getColorPaletteDisplay(): String =
                when (colorPalette) {
                    "iron" -> "Iron"
                    "rainbow" -> "Rainbow"
                    "grayscale" -> "Grayscale"
                    "hot_metal" -> "Hot Metal"
                    "arctic" -> "Arctic"
                    "medical" -> "Medical"
                    else -> colorPalette
                }

            /**
             * Get temperature range values in Celsius
             */
            fun getTemperatureRangeValues(): Pair<Float, Float>? =
                when (temperatureRange) {
                    "-20_150" -> Pair(-20f, 150f)
                    "0_100" -> Pair(0f, 100f)
                    "15_45" -> Pair(15f, 45f)
                    "20_40" -> Pair(20f, 40f)
                    else -> null // Auto or custom ranges
                }

            /**
             * Convert temperature from Celsius to selected units
             */
            fun convertTemperature(celsius: Float): Float =
                when (temperatureUnits) {
                    "fahrenheit" -> celsius * 9f / 5f + 32f
                    "kelvin" -> celsius + 273.15f
                    else -> celsius // Celsius
                }

            /**
             * Get temperature unit symbol
             */
            fun getTemperatureUnitSymbol(): String =
                when (temperatureUnits) {
                    "fahrenheit" -> "°F"
                    "kelvin" -> "K"
                    else -> "°C"
                }

            /**
             * Check if radiometric data should be saved
             */
            fun shouldSaveRadiometricData(): Boolean = dataFormat == "radiometric" || dataFormat == "combined"

            /**
             * Check if visual data should be saved
             */
            fun shouldSaveVisualData(): Boolean = dataFormat == "visual" || dataFormat == "combined"

            /**
             * Check if raw sensor data should be saved
             */
            fun shouldSaveRawData(): Boolean = dataFormat == "raw"
        }

        /**
         * Get current thermal camera configuration
         */
        fun getCurrentConfig(): ThermalConfig =
            ThermalConfig(
                isEnabled = prefs.getBoolean(KEY_THERMAL_ENABLED, true),
                frameRate = prefs.getString(KEY_THERMAL_FRAME_RATE, DEFAULT_FRAME_RATE.toString())?.toIntOrNull() ?: DEFAULT_FRAME_RATE,
                colorPalette = prefs.getString(KEY_THERMAL_COLOR_PALETTE, DEFAULT_COLOR_PALETTE) ?: DEFAULT_COLOR_PALETTE,
                temperatureRange = prefs.getString(KEY_THERMAL_TEMP_RANGE, DEFAULT_TEMP_RANGE) ?: DEFAULT_TEMP_RANGE,
                emissivity = prefs.getString(KEY_THERMAL_EMISSIVITY, DEFAULT_EMISSIVITY.toString())?.toFloatOrNull() ?: DEFAULT_EMISSIVITY,
                autoCalibration = prefs.getBoolean(KEY_THERMAL_AUTO_CALIBRATION, true),
                highResolution = prefs.getBoolean(KEY_THERMAL_HIGH_RESOLUTION, false),
                temperatureUnits = prefs.getString(KEY_THERMAL_TEMP_UNITS, DEFAULT_TEMP_UNITS) ?: DEFAULT_TEMP_UNITS,
                usbPriority = prefs.getBoolean(KEY_THERMAL_USB_PRIORITY, true),
                dataFormat = prefs.getString(KEY_THERMAL_DATA_FORMAT, DEFAULT_DATA_FORMAT) ?: DEFAULT_DATA_FORMAT,
            )

        /**
         * Update thermal camera configuration
         */
        fun updateConfig(config: ThermalConfig) {
            prefs.edit().apply {
                putBoolean(KEY_THERMAL_ENABLED, config.isEnabled)
                putString(KEY_THERMAL_FRAME_RATE, config.frameRate.toString())
                putString(KEY_THERMAL_COLOR_PALETTE, config.colorPalette)
                putString(KEY_THERMAL_TEMP_RANGE, config.temperatureRange)
                putString(KEY_THERMAL_EMISSIVITY, config.emissivity.toString())
                putBoolean(KEY_THERMAL_AUTO_CALIBRATION, config.autoCalibration)
                putBoolean(KEY_THERMAL_HIGH_RESOLUTION, config.highResolution)
                putString(KEY_THERMAL_TEMP_UNITS, config.temperatureUnits)
                putBoolean(KEY_THERMAL_USB_PRIORITY, config.usbPriority)
                putString(KEY_THERMAL_DATA_FORMAT, config.dataFormat)
                apply()
            }
        }

        /**
         * Check if thermal recording is enabled
         */
        fun isThermalRecordingEnabled(): Boolean = prefs.getBoolean(KEY_THERMAL_ENABLED, true)

        /**
         * Get thermal frame rate
         */
        fun getFrameRate(): Int = prefs.getString(KEY_THERMAL_FRAME_RATE, DEFAULT_FRAME_RATE.toString())?.toIntOrNull() ?: DEFAULT_FRAME_RATE

        /**
         * Get thermal color palette
         */
        fun getColorPalette(): String = prefs.getString(KEY_THERMAL_COLOR_PALETTE, DEFAULT_COLOR_PALETTE) ?: DEFAULT_COLOR_PALETTE

        /**
         * Get thermal emissivity
         */
        fun getEmissivity(): Float = prefs.getString(KEY_THERMAL_EMISSIVITY, DEFAULT_EMISSIVITY.toString())?.toFloatOrNull() ?: DEFAULT_EMISSIVITY

        /**
         * Check if USB priority mode is enabled
         */
        fun isUsbPriorityEnabled(): Boolean = prefs.getBoolean(KEY_THERMAL_USB_PRIORITY, true)

        /**
         * Check if auto-calibration is enabled
         */
        fun isAutoCalibrationEnabled(): Boolean = prefs.getBoolean(KEY_THERMAL_AUTO_CALIBRATION, true)

        /**
         * Check if high-resolution mode is enabled
         */
        fun isHighResolutionEnabled(): Boolean = prefs.getBoolean(KEY_THERMAL_HIGH_RESOLUTION, false)

        /**
         * Get thermal data format
         */
        fun getDataFormat(): String = prefs.getString(KEY_THERMAL_DATA_FORMAT, DEFAULT_DATA_FORMAT) ?: DEFAULT_DATA_FORMAT

        /**
         * Get temperature units
         */
        fun getTemperatureUnits(): String = prefs.getString(KEY_THERMAL_TEMP_UNITS, DEFAULT_TEMP_UNITS) ?: DEFAULT_TEMP_UNITS

        /**
         * Register preference change listener
         */
        fun registerOnSharedPreferenceChangeListener(listener: SharedPreferences.OnSharedPreferenceChangeListener) {
            prefs.registerOnSharedPreferenceChangeListener(listener)
        }

        /**
         * Unregister preference change listener
         */
        fun unregisterOnSharedPreferenceChangeListener(listener: SharedPreferences.OnSharedPreferenceChangeListener) {
            prefs.unregisterOnSharedPreferenceChangeListener(listener)
        }

        /**
         * Generate configuration summary for logging
         */
        fun getConfigSummary(): String {
            val config = getCurrentConfig()
            return buildString {
                appendLine("=== Thermal Camera Configuration ===")
                appendLine("Enabled: ${config.isEnabled}")
                appendLine("Frame Rate: ${config.frameRate} fps")
                appendLine("Color Palette: ${config.getColorPaletteDisplay()}")
                appendLine("Temperature Range: ${config.getTemperatureRangeDisplay()}")
                appendLine("Emissivity: ${config.emissivity}")
                appendLine("Auto-Calibration: ${config.autoCalibration}")
                appendLine("High Resolution: ${config.highResolution}")
                appendLine("Temperature Units: ${config.getTemperatureUnitSymbol()}")
                appendLine("USB Priority: ${config.usbPriority}")
                appendLine("Data Format: ${config.dataFormat}")
                appendLine("========================================")
            }
        }

        /**
         * Export configuration to string for session metadata
         */
        fun exportConfigToString(): String {
            val config = getCurrentConfig()
            return "thermal_enabled=${config.isEnabled}," +
                "frame_rate=${config.frameRate}," +
                "color_palette=${config.colorPalette}," +
                "temp_range=${config.temperatureRange}," +
                "emissivity=${config.emissivity}," +
                "auto_calibration=${config.autoCalibration}," +
                "high_resolution=${config.highResolution}," +
                "temp_units=${config.temperatureUnits}," +
                "usb_priority=${config.usbPriority}," +
                "data_format=${config.dataFormat}"
        }
    }