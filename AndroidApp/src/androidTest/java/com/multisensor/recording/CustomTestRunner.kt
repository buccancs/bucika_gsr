package com.multisensor.recording

import android.app.Application
import android.content.Context
import androidx.test.runner.AndroidJUnitRunner
import dagger.hilt.android.testing.HiltTestApplication

/**
 * A custom test runner for Hilt to replace the production Application class
 * with Hilt's HiltTestApplication in instrumentation tests.
 *
 * This runner ensures that Hilt tests use HiltTestApplication instead of
 * the production MultiSensorApplication, which is required for proper
 * Hilt testing functionality.
 */
class CustomTestRunner : AndroidJUnitRunner() {
    override fun newApplication(
        cl: ClassLoader?,
        className: String?,
        context: Context?,
    ): Application {
        // Replace the production application with HiltTestApplication
        return super.newApplication(cl, HiltTestApplication::class.java.name, context)
    }
}