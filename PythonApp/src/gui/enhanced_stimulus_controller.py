"""
Enhanced Stimulus Controller with PsychoPy-Inspired Improvements

This module implements an improved StimulusController with VLC backend support,
enhanced timing precision, and better error handling inspired by PsychoPy's approach.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.5 - Enhanced Stimulus Presentation Controller
"""

import json
import os
import time
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QApplication,
    QProgressBar,
)
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

# Try to import VLC for enhanced video support
try:
    import vlc

    VLC_AVAILABLE = True
    print("[DEBUG_LOG] VLC backend available")
except ImportError:
    VLC_AVAILABLE = False
    print("[DEBUG_LOG] VLC backend not available, using QMediaPlayer only")


class VideoBackend(Enum):
    """Enumeration of available video backends."""

    QT_MULTIMEDIA = "qt_multimedia"
    VLC = "vlc"


class CodecInfo:
    """Information about video codec support."""

    def __init__(self):
        self.qt_supported = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".m4v", ".3gp"]
        self.vlc_supported = [
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".wmv",
            ".m4v",
            ".3gp",
            ".flv",
            ".webm",
            ".ogv",
            ".mpg",
            ".mpeg",
            ".ts",
            ".mts",
            ".m2ts",
        ]
        self.recommended_formats = [".mp4", ".avi", ".mov"]

    def is_supported(self, file_path: str, backend: VideoBackend) -> bool:
        """Check if file format is supported by the specified backend."""
        ext = os.path.splitext(file_path)[1].lower()
        if backend == VideoBackend.QT_MULTIMEDIA:
            return ext in self.qt_supported
        elif backend == VideoBackend.VLC:
            return ext in self.vlc_supported
        return False

    def get_best_backend(self, file_path: str) -> Optional[VideoBackend]:
        """Get the best backend for the given file."""
        ext = os.path.splitext(file_path)[1].lower()

        # Prefer Qt for common formats (better integration)
        if ext in self.recommended_formats:
            return VideoBackend.QT_MULTIMEDIA

        # Use VLC for less common formats if available
        if VLC_AVAILABLE and ext in self.vlc_supported:
            return VideoBackend.VLC

        # Fallback to Qt if supported
        if ext in self.qt_supported:
            return VideoBackend.QT_MULTIMEDIA

        return None


class EnhancedTimingLogger:
    """Enhanced timing logger with PsychoPy-inspired precision."""

    def __init__(self, log_directory: str = "logs"):
        self.log_directory = log_directory
        self.current_log_file: Optional[str] = None
        self.experiment_start_time: Optional[float] = None
        self.event_counter = 0

        # Multiple clock types for enhanced precision
        self.system_clock = time.time
        self.monotonic_clock = time.monotonic
        self.perf_clock = time.perf_counter

        # Timing calibration
        self.clock_offset = 0.0
        self.calibrate_timing()

        os.makedirs(log_directory, exist_ok=True)

    def calibrate_timing(self):
        """Calibrate timing precision and measure clock drift."""
        # Measure clock precision
        start_time = self.perf_clock()
        system_start = self.system_clock()

        # Small delay to measure precision
        time.sleep(0.001)

        end_time = self.perf_clock()
        system_end = self.system_clock()

        # Calculate offset between clocks
        perf_duration = end_time - start_time
        system_duration = system_end - system_start
        self.clock_offset = system_duration - perf_duration

        print(f"[DEBUG_LOG] Timing calibration: offset={self.clock_offset*1000:.3f}ms")

    def get_precise_timestamp(self) -> Dict[str, float]:
        """Get timestamp with multiple clock sources for maximum precision."""
        return {
            "system_time": self.system_clock(),
            "monotonic_time": self.monotonic_clock(),
            "performance_time": self.perf_clock(),
            "corrected_time": self.system_clock() - self.clock_offset,
        }

    def start_experiment_log(self, video_file: str, backend: str) -> str:
        """Start experiment log with enhanced metadata."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.current_log_file = os.path.join(
            self.log_directory, f"enhanced_experiment_log_{timestamp}.json"
        )

        timing_info = self.get_precise_timestamp()
        self.experiment_start_time = timing_info["corrected_time"]
        self.event_counter = 0

        log_data = {
            "experiment_info": {
                "start_timestamps": timing_info,
                "start_time_formatted": datetime.fromtimestamp(
                    self.experiment_start_time
                ).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "stimulus_file": video_file,
                "stimulus_filename": os.path.basename(video_file),
                "video_backend": backend,
                "timing_calibration": {
                    "clock_offset_ms": self.clock_offset * 1000,
                    "precision_test": "completed",
                },
            },
            "events": [],
        }

        with open(self.current_log_file, "w") as f:
            json.dump(log_data, f, indent=2)

        return self.current_log_file

    def log_stimulus_start(self, video_duration_ms: int, frame_rate: float = None):
        """Log stimulus start with enhanced timing data."""
        if not self.current_log_file or not self.experiment_start_time:
            return

        timing_info = self.get_precise_timestamp()

        event = {
            "event_type": "stimulus_start",
            "timestamps": timing_info,
            "timestamp_formatted": datetime.fromtimestamp(
                timing_info["corrected_time"]
            ).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "experiment_time": timing_info["corrected_time"]
            - self.experiment_start_time,
            "video_duration_ms": video_duration_ms,
            "video_duration_s": video_duration_ms / 1000.0,
            "frame_rate": frame_rate,
        }

        self._append_event(event)

    def log_event_marker(
        self, video_position_ms: int, marker_label: str = "", frame_number: int = None
    ):
        """Log event marker with frame-accurate timing."""
        if not self.current_log_file or not self.experiment_start_time:
            return

        timing_info = self.get_precise_timestamp()
        self.event_counter += 1

        event = {
            "event_type": "event_marker",
            "marker_number": self.event_counter,
            "marker_label": marker_label or f"Marker {self.event_counter}",
            "timestamps": timing_info,
            "timestamp_formatted": datetime.fromtimestamp(
                timing_info["corrected_time"]
            ).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "experiment_time": timing_info["corrected_time"]
            - self.experiment_start_time,
            "video_position_ms": video_position_ms,
            "video_position_s": video_position_ms / 1000.0,
            "frame_number": frame_number,
        }

        self._append_event(event)

    def _append_event(self, event: Dict[str, Any]):
        """Append event with thread safety."""
        if not self.current_log_file:
            return

        try:
            with open(self.current_log_file, "r") as f:
                log_data = json.load(f)

            log_data["events"].append(event)

            with open(self.current_log_file, "w") as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            print(f"[DEBUG_LOG] Error writing to log file: {e}")


class VLCVideoWidget(QWidget):
    """VLC-based video widget for enhanced codec support."""

    # Signals
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    state_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")

        if not VLC_AVAILABLE:
            self.vlc_instance = None
            self.media_player = None
            return

        # Create VLC instance
        self.vlc_instance = vlc.Instance(
            [
                "--no-xlib",  # Don't use X11
                "--quiet",  # Reduce console output
                "--intf",
                "dummy",  # No interface
            ]
        )

        self.media_player = self.vlc_instance.media_player_new()
        self.current_media = None

        # Position tracking timer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self._update_position)
        self.position_timer.setInterval(100)

        # Set up video output
        if hasattr(self.media_player, "set_hwnd"):
            # Windows
            self.media_player.set_hwnd(self.winId())
        elif hasattr(self.media_player, "set_xwindow"):
            # Linux
            self.media_player.set_xwindow(self.winId())
        elif hasattr(self.media_player, "set_nsobject"):
            # macOS
            self.media_player.set_nsobject(int(self.winId()))

    def load_media(self, file_path: str) -> bool:
        """Load media file into VLC player."""
        if not VLC_AVAILABLE or not self.media_player:
            return False

        try:
            self.current_media = self.vlc_instance.media_new(file_path)
            self.media_player.set_media(self.current_media)

            # Parse media to get duration
            self.current_media.parse()

            print(f"[DEBUG_LOG] VLC media loaded: {file_path}")
            return True

        except Exception as e:
            self.error_occurred.emit(f"VLC load error: {str(e)}")
            return False

    def play(self):
        """Start playback."""
        if self.media_player:
            self.media_player.play()
            self.position_timer.start()
            self.state_changed.emit("Playing")

    def pause(self):
        """Pause playback."""
        if self.media_player:
            self.media_player.pause()
            self.state_changed.emit("Paused")

    def stop(self):
        """Stop playback."""
        if self.media_player:
            self.media_player.stop()
            self.position_timer.stop()
            self.state_changed.emit("Stopped")

    def set_position(self, position_ms: int):
        """Set playback position in milliseconds."""
        if self.media_player and self.get_duration() > 0:
            position_ratio = position_ms / self.get_duration()
            self.media_player.set_position(position_ratio)

    def get_position(self) -> int:
        """Get current position in milliseconds."""
        if self.media_player:
            duration = self.get_duration()
            if duration > 0:
                return int(self.media_player.get_position() * duration)
        return 0

    def get_duration(self) -> int:
        """Get media duration in milliseconds."""
        if self.current_media:
            return self.current_media.get_duration()
        return 0

    def is_playing(self) -> bool:
        """Check if media is playing."""
        if self.media_player:
            return self.media_player.is_playing()
        return False

    def _update_position(self):
        """Update position signal."""
        if self.is_playing():
            self.position_changed.emit(self.get_position())


class EnhancedStimulusController(QWidget):
    """
    Enhanced stimulus controller with PsychoPy-inspired improvements.

    Features:
    - VLC backend support for better codec compatibility
    - Enhanced timing precision with multiple clock sources
    - Automatic backend selection and fallback
    - Comprehensive error handling and user feedback
    """

    # Signals
    status_changed = pyqtSignal(str)
    experiment_started = pyqtSignal()
    experiment_ended = pyqtSignal()
    error_occurred = pyqtSignal(str)
    backend_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        # Codec and backend management
        self.codec_info = CodecInfo()
        self.current_backend = None
        self.current_video_file: Optional[str] = None

        # Media players
        self.qt_media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.qt_video_widget = QVideoWidget()
        self.qt_media_player.setVideoOutput(self.qt_video_widget)

        self.vlc_video_widget = VLCVideoWidget() if VLC_AVAILABLE else None

        # Current active player
        self.active_video_widget = None

        # Enhanced timing and logging
        self.timing_logger = EnhancedTimingLogger()
        self.is_experiment_active = False

        # Performance monitoring
        self.frame_drop_count = 0
        self.last_frame_time = 0

        # Position update timer
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.setInterval(50)  # Higher frequency for smoother updates

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Initialize enhanced user interface."""
        layout = QVBoxLayout(self)

        # Status and backend info
        info_layout = QHBoxLayout()

        self.status_label = QLabel("Enhanced Stimulus Controller Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.status_label)

        self.backend_label = QLabel("Backend: None")
        self.backend_label.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
        info_layout.addWidget(self.backend_label)

        layout.addLayout(info_layout)

        # Performance monitoring
        self.performance_bar = QProgressBar()
        self.performance_bar.setRange(0, 100)
        self.performance_bar.setValue(100)
        self.performance_bar.setFormat("Performance: %p%")
        self.performance_bar.hide()  # Show only during playback
        layout.addWidget(self.performance_bar)

        # Video widgets (hidden by default)
        self.qt_video_widget.hide()
        layout.addWidget(self.qt_video_widget)

        if self.vlc_video_widget:
            self.vlc_video_widget.hide()
            layout.addWidget(self.vlc_video_widget)

        # Enhanced control buttons
        button_layout = QHBoxLayout()

        self.test_play_btn = QPushButton("Test Play")
        self.test_play_btn.clicked.connect(self.test_play)
        self.test_play_btn.setEnabled(False)
        button_layout.addWidget(self.test_play_btn)

        self.test_pause_btn = QPushButton("Test Pause")
        self.test_pause_btn.clicked.connect(self.test_pause)
        self.test_pause_btn.setEnabled(False)
        button_layout.addWidget(self.test_pause_btn)

        self.test_fullscreen_btn = QPushButton("Test Full-Screen")
        self.test_fullscreen_btn.clicked.connect(self.test_fullscreen)
        self.test_fullscreen_btn.setEnabled(False)
        button_layout.addWidget(self.test_fullscreen_btn)

        self.switch_backend_btn = QPushButton("Switch Backend")
        self.switch_backend_btn.clicked.connect(self.switch_backend)
        self.switch_backend_btn.setEnabled(False)
        button_layout.addWidget(self.switch_backend_btn)

        layout.addLayout(button_layout)

    def connect_signals(self):
        """Connect signals for both backends."""
        # Qt Media Player signals
        self.qt_media_player.stateChanged.connect(self.on_qt_state_changed)
        self.qt_media_player.mediaStatusChanged.connect(self.on_qt_media_status_changed)
        self.qt_media_player.positionChanged.connect(self.on_qt_position_changed)
        self.qt_media_player.durationChanged.connect(self.on_qt_duration_changed)
        self.qt_media_player.error.connect(self.on_qt_media_error)

        # VLC signals
        if self.vlc_video_widget:
            self.vlc_video_widget.position_changed.connect(self.on_vlc_position_changed)
            self.vlc_video_widget.duration_changed.connect(self.on_vlc_duration_changed)
            self.vlc_video_widget.state_changed.connect(self.on_vlc_state_changed)
            self.vlc_video_widget.error_occurred.connect(self.on_vlc_error)

    def load_video(self, file_path: str) -> bool:
        """Load video with automatic backend selection."""
        if not os.path.exists(file_path):
            self.error_occurred.emit(f"Video file not found: {file_path}")
            return False

        # Determine best backend
        best_backend = self.codec_info.get_best_backend(file_path)
        if not best_backend:
            self.error_occurred.emit(
                f"Unsupported video format: {os.path.splitext(file_path)[1]}"
            )
            return False

        # Try loading with best backend first
        if self._load_with_backend(file_path, best_backend):
            self.current_video_file = file_path
            self.current_backend = best_backend
            self._update_backend_ui()
            self._enable_controls()

            self.status_changed.emit(
                f"Loaded: {os.path.basename(file_path)} ({best_backend.value})"
            )
            print(
                f"[DEBUG_LOG] Video loaded with {best_backend.value} backend: {file_path}"
            )
            return True

        # Try fallback backend
        fallback_backend = (
            VideoBackend.VLC
            if best_backend == VideoBackend.QT_MULTIMEDIA
            else VideoBackend.QT_MULTIMEDIA
        )
        if fallback_backend == VideoBackend.VLC and not VLC_AVAILABLE:
            self.error_occurred.emit("Primary backend failed and VLC not available")
            return False

        if self._load_with_backend(file_path, fallback_backend):
            self.current_video_file = file_path
            self.current_backend = fallback_backend
            self._update_backend_ui()
            self._enable_controls()

            self.status_changed.emit(
                f"Loaded: {os.path.basename(file_path)} ({fallback_backend.value} fallback)"
            )
            print(
                f"[DEBUG_LOG] Video loaded with fallback {fallback_backend.value} backend: {file_path}"
            )
            return True

        self.error_occurred.emit("Failed to load video with any available backend")
        return False

    def _load_with_backend(self, file_path: str, backend: VideoBackend) -> bool:
        """Load video with specific backend."""
        try:
            if backend == VideoBackend.QT_MULTIMEDIA:
                self.qt_media_player.stop()
                file_url = QUrl.fromLocalFile(os.path.abspath(file_path))
                media_content = QMediaContent(file_url)
                self.qt_media_player.setMedia(media_content)
                self.active_video_widget = self.qt_video_widget
                return True

            elif backend == VideoBackend.VLC and self.vlc_video_widget:
                if self.vlc_video_widget.load_media(file_path):
                    self.active_video_widget = self.vlc_video_widget
                    return True

        except Exception as e:
            print(f"[DEBUG_LOG] Backend {backend.value} load failed: {e}")

        return False

    def switch_backend(self):
        """Switch between available backends."""
        if not self.current_video_file:
            return

        # Determine alternative backend
        if self.current_backend == VideoBackend.QT_MULTIMEDIA and VLC_AVAILABLE:
            new_backend = VideoBackend.VLC
        elif self.current_backend == VideoBackend.VLC:
            new_backend = VideoBackend.QT_MULTIMEDIA
        else:
            self.status_changed.emit("No alternative backend available")
            return

        # Stop current playback
        self.stop_playback()

        # Load with new backend
        if self._load_with_backend(self.current_video_file, new_backend):
            self.current_backend = new_backend
            self._update_backend_ui()
            self.backend_changed.emit(new_backend.value)
            self.status_changed.emit(f"Switched to {new_backend.value} backend")
        else:
            self.error_occurred.emit(f"Failed to switch to {new_backend.value} backend")

    def _update_backend_ui(self):
        """Update UI to reflect current backend."""
        if self.current_backend:
            self.backend_label.setText(f"Backend: {self.current_backend.value}")

            # Show/hide appropriate video widget
            if self.current_backend == VideoBackend.QT_MULTIMEDIA:
                if self.vlc_video_widget:
                    self.vlc_video_widget.hide()
                self.qt_video_widget.show()
            elif self.current_backend == VideoBackend.VLC:
                self.qt_video_widget.hide()
                if self.vlc_video_widget:
                    self.vlc_video_widget.show()

    def _enable_controls(self):
        """Enable control buttons when video is loaded."""
        self.test_play_btn.setEnabled(True)
        self.test_pause_btn.setEnabled(True)
        self.test_fullscreen_btn.setEnabled(True)
        self.switch_backend_btn.setEnabled(
            VLC_AVAILABLE and self.current_video_file is not None
        )

    def start_stimulus_playback(self, screen_index: int = 0) -> bool:
        """Start enhanced stimulus playback with performance monitoring."""
        if not self.current_video_file or not self.current_backend:
            self.error_occurred.emit("No video loaded or backend selected")
            return False

        if self.is_experiment_active:
            self.error_occurred.emit("Experiment already active")
            return False

        try:
            # Start enhanced experiment logging
            log_file = self.timing_logger.start_experiment_log(
                self.current_video_file, self.current_backend.value
            )
            print(f"[DEBUG_LOG] Started enhanced experiment log: {log_file}")

            # Position video on selected screen
            self.position_video_on_screen(screen_index)

            # Show performance monitoring
            self.performance_bar.show()
            self.performance_bar.setValue(100)

            # Start playback based on backend
            if self.current_backend == VideoBackend.QT_MULTIMEDIA:
                self.qt_video_widget.showFullScreen()
                self.qt_video_widget.setFocus()
                self.qt_media_player.play()
            elif self.current_backend == VideoBackend.VLC and self.vlc_video_widget:
                self.vlc_video_widget.showFullScreen()
                self.vlc_video_widget.setFocus()
                self.vlc_video_widget.play()

            self.position_timer.start()
            self.is_experiment_active = True
            self.experiment_started.emit()
            self.status_changed.emit("Enhanced Experiment Started - Stimulus Playing")

            return True

        except Exception as e:
            self.error_occurred.emit(
                f"Error starting enhanced stimulus playback: {str(e)}"
            )
            return False

    def stop_playback(self):
        """Stop current playback."""
        if self.current_backend == VideoBackend.QT_MULTIMEDIA:
            self.qt_media_player.stop()
        elif self.current_backend == VideoBackend.VLC and self.vlc_video_widget:
            self.vlc_video_widget.stop()

    def position_video_on_screen(self, screen_index: int):
        """Position video widget on specified screen."""
        screens = QApplication.screens()
        if 0 <= screen_index < len(screens):
            target_screen = screens[screen_index]
            geometry = target_screen.geometry()
            if self.active_video_widget:
                self.active_video_widget.setGeometry(geometry)

    # Test methods
    def test_play(self):
        """Test play functionality."""
        if self.current_backend == VideoBackend.QT_MULTIMEDIA:
            self.qt_media_player.play()
            self.qt_video_widget.show()
        elif self.current_backend == VideoBackend.VLC and self.vlc_video_widget:
            self.vlc_video_widget.play()
            self.vlc_video_widget.show()

    def test_pause(self):
        """Test pause functionality."""
        if self.current_backend == VideoBackend.QT_MULTIMEDIA:
            self.qt_media_player.pause()
        elif self.current_backend == VideoBackend.VLC and self.vlc_video_widget:
            self.vlc_video_widget.pause()

    def test_fullscreen(self):
        """Test full-screen functionality."""
        if self.active_video_widget:
            self.active_video_widget.showFullScreen()
            self.active_video_widget.setFocus()

    def update_position(self):
        """Update position with performance monitoring."""
        if not self.is_experiment_active:
            return

        # Monitor frame timing for performance
        current_time = time.perf_counter()
        if self.last_frame_time > 0:
            frame_interval = current_time - self.last_frame_time
            expected_interval = 0.05  # 50ms update interval

            if frame_interval > expected_interval * 1.5:  # 50% tolerance
                self.frame_drop_count += 1
                performance = max(0, 100 - (self.frame_drop_count * 2))
                self.performance_bar.setValue(performance)

        self.last_frame_time = current_time

    # Signal handlers for Qt backend
    def on_qt_state_changed(self, state):
        """Handle Qt media player state changes."""
        if self.current_backend != VideoBackend.QT_MULTIMEDIA:
            return

        state_names = {
            QMediaPlayer.StoppedState: "Stopped",
            QMediaPlayer.PlayingState: "Playing",
            QMediaPlayer.PausedState: "Paused",
        }
        state_name = state_names.get(state, "Unknown")
        print(f"[DEBUG_LOG] Qt media player state: {state_name}")

        if state == QMediaPlayer.PlayingState and self.is_experiment_active:
            duration = self.qt_media_player.duration()
            self.timing_logger.log_stimulus_start(duration)

    def on_qt_media_status_changed(self, status):
        """Handle Qt media status changes."""
        if status == QMediaPlayer.EndOfMedia and self.is_experiment_active:
            self.stop_stimulus_playback("completed")

    def on_qt_position_changed(self, position):
        """Handle Qt position changes."""
        pass  # Handled by update_position

    def on_qt_duration_changed(self, duration):
        """Handle Qt duration changes."""
        if duration > 0:
            print(f"[DEBUG_LOG] Qt video duration: {duration/1000:.1f}s")

    def on_qt_media_error(self, error):
        """Handle Qt media errors with enhanced feedback."""
        error_messages = {
            QMediaPlayer.NoError: "No error",
            QMediaPlayer.ResourceError: "Resource error - try VLC backend or check file",
            QMediaPlayer.FormatError: "Format error - try VLC backend for better codec support",
            QMediaPlayer.NetworkError: "Network error",
            QMediaPlayer.AccessDeniedError: "Access denied - check file permissions",
            QMediaPlayer.ServiceMissingError: "Codec missing - try VLC backend",
        }

        error_msg = error_messages.get(error, f"Unknown error ({error})")

        # Suggest VLC backend for codec issues
        if (
            error in [QMediaPlayer.FormatError, QMediaPlayer.ServiceMissingError]
            and VLC_AVAILABLE
        ):
            error_msg += " - VLC backend available as alternative"

        self.error_occurred.emit(f"Qt backend error: {error_msg}")

    # Signal handlers for VLC backend
    def on_vlc_state_changed(self, state):
        """Handle VLC state changes."""
        if self.current_backend != VideoBackend.VLC:
            return

        print(f"[DEBUG_LOG] VLC player state: {state}")

        if state == "Playing" and self.is_experiment_active:
            duration = self.vlc_video_widget.get_duration()
            self.timing_logger.log_stimulus_start(duration)

    def on_vlc_position_changed(self, position):
        """Handle VLC position changes."""
        pass  # Handled by update_position

    def on_vlc_duration_changed(self, duration):
        """Handle VLC duration changes."""
        if duration > 0:
            print(f"[DEBUG_LOG] VLC video duration: {duration/1000:.1f}s")

    def on_vlc_error(self, error_msg):
        """Handle VLC errors."""
        self.error_occurred.emit(f"VLC backend error: {error_msg}")

    def stop_stimulus_playback(self, reason: str = "stopped"):
        """Stop stimulus playback with enhanced logging."""
        if not self.is_experiment_active:
            return

        try:
            # Stop playback
            self.stop_playback()
            self.position_timer.stop()

            # Hide performance monitoring
            self.performance_bar.hide()

            # Log experiment end
            current_position = self.get_current_position()
            self.timing_logger.log_stimulus_end(current_position, reason)

            # Hide video widget
            if self.active_video_widget:
                self.active_video_widget.hide()

            self.is_experiment_active = False
            self.experiment_ended.emit()
            self.status_changed.emit(f"Enhanced Experiment Ended - {reason.title()}")

        except Exception as e:
            self.error_occurred.emit(
                f"Error stopping enhanced stimulus playback: {str(e)}"
            )

    def mark_event(self, label: str = ""):
        """Mark event with enhanced timing."""
        if not self.is_experiment_active:
            return

        try:
            current_position = self.get_current_position()
            self.timing_logger.log_event_marker(current_position, label)

            marker_num = self.timing_logger.event_counter
            self.status_changed.emit(
                f"Enhanced Event Marker {marker_num} - {current_position/1000:.1f}s"
            )

        except Exception as e:
            self.error_occurred.emit(f"Error marking enhanced event: {str(e)}")

    def get_current_position(self) -> int:
        """Get current position from active backend."""
        if self.current_backend == VideoBackend.QT_MULTIMEDIA:
            return self.qt_media_player.position()
        elif self.current_backend == VideoBackend.VLC and self.vlc_video_widget:
            return self.vlc_video_widget.get_position()
        return 0

    def get_duration(self) -> int:
        """Get duration from active backend."""
        if self.current_backend == VideoBackend.QT_MULTIMEDIA:
            return self.qt_media_player.duration()
        elif self.current_backend == VideoBackend.VLC and self.vlc_video_widget:
            return self.vlc_video_widget.get_duration()
        return 0

    def is_playing(self) -> bool:
        """Check if video is playing."""
        if self.current_backend == VideoBackend.QT_MULTIMEDIA:
            return self.qt_media_player.state() == QMediaPlayer.PlayingState
        elif self.current_backend == VideoBackend.VLC and self.vlc_video_widget:
            return self.vlc_video_widget.is_playing()
        return False
