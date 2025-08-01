"""
Calibration Manager for Multi-Sensor Recording System Controller

This module implements the CalibrationManager class for Milestone 3.4: Calibration Engine (OpenCV).
It provides comprehensive calibration workflow using OpenCV to align RGB and thermal cameras
on each phone, including pattern detection, intrinsic/extrinsic calibration, and overlay functionality.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.4 - Calibration Engine (OpenCV)
"""

import cv2
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .calibration_processor import CalibrationProcessor
from .calibration_result import CalibrationResult

# Import centralized logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)


class CalibrationManager:
    """
    Main calibration manager that orchestrates the entire calibration workflow.

    This class handles:
    - Calibration session management
    - Image capture coordination with Android devices
    - OpenCV calibration computations
    - Results storage and loading
    - Real-time overlay functionality
    """

    def __init__(self, output_dir: str = "calibration_data"):
        self.logger = get_logger(__name__)
        self.logger.info(f"for initialized")
        """
        Initialize calibration manager.

        Args:
            output_dir (str): Directory to store calibration data and images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Calibration processor for OpenCV operations
        self.processor = CalibrationProcessor()

        # Current calibration session data
        self.current_session = None
        self.captured_images = {}  # device_id -> {'rgb': [], 'thermal': []}
        self.captured_frames = []  # Backward compatibility for tests
        self.calibration_results = {}  # device_id -> CalibrationResult

        # Calibration pattern settings
        self.pattern_type = "chessboard"
        self.chessboard_size = (9, 6)  # Internal corners (width, height)
        self.square_size = 25.0  # Square size in mm
        self.min_images = 10  # Minimum images required for calibration

        # Status tracking
        self.is_capturing = False
        self.capture_count = {}  # device_id -> count

        logger.info(f"CalibrationManager initialized with output directory: {self.output_dir}")
        logger.debug(f"Pattern: {self.pattern_type}, Size: {self.chessboard_size}, Square: {self.square_size}mm")

    def start_calibration_session(
        self, device_ids: List[str], session_name: str = None
    ) -> Dict[str, Any]:
        """
        Start a new calibration session.

        Args:
            device_ids (List[str]): List of device IDs to calibrate
            session_name (str, optional): Custom session name

        Returns:
            Dict: Session information
        """
        logger.info(f"Starting calibration session for devices: {device_ids}")
        
        if self.is_capturing:
            logger.error("Attempted to start calibration session while another is in progress")
            raise RuntimeError("Calibration session already in progress")

        # Generate session info
        timestamp = datetime.now()
        if session_name is None:
            session_name = f"calibration_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        session_folder = self.output_dir / session_name
        session_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created session folder: {session_folder}")

        self.current_session = {
            "session_name": session_name,
            "session_folder": str(session_folder),
            "device_ids": device_ids,
            "start_time": timestamp.isoformat(),
            "pattern_type": self.pattern_type,
            "pattern_size": self.chessboard_size,
            "square_size": self.square_size,
            "status": "active",
        }

        # Initialize capture data for each device
        for device_id in device_ids:
            self.captured_images[device_id] = {"rgb": [], "thermal": []}
            self.capture_count[device_id] = 0

        # Save session metadata
        session_file = session_folder / "session_info.json"
        with open(session_file, "w") as f:
            json.dump(self.current_session, f, indent=2)

        print(f"[DEBUG_LOG] Calibration session started: {session_name}")
        return self.current_session

    def capture_calibration_frame(self, device_server) -> Dict[str, Any]:
        """
        Capture calibration frames from all devices in current session.

        Args:
            device_server: JsonSocketServer instance for device communication

        Returns:
            Dict: Capture results with success status and frame counts
        """
        if not self.current_session:
            raise RuntimeError("No active calibration session")

        if self.is_capturing:
            return {"success": False, "message": "Capture already in progress"}

        self.is_capturing = True
        capture_results = {
            "success": True,
            "message": "Calibration frames captured successfully",
            "device_results": {},
            "total_frames": {},
        }

        try:
            # Send capture command to all devices
            capture_command = {
                "cmd": "capture_calibration",
                "session_id": self.current_session["session_name"],
                "pattern_type": self.pattern_type,
                "pattern_size": self.chessboard_size,
            }

            device_count = device_server.broadcast_command(capture_command)
            print(
                f"[DEBUG_LOG] Sent calibration capture command to {device_count} devices"
            )

            # Wait for responses (this would be handled by device server callbacks in real implementation)
            # For now, simulate successful capture
            for device_id in self.current_session["device_ids"]:
                # In real implementation, this would receive actual images from devices
                success = self._simulate_image_capture(device_id)

                if success:
                    self.capture_count[device_id] += 1
                    capture_results["device_results"][device_id] = {
                        "success": True,
                        "message": "Frame captured successfully",
                    }
                else:
                    capture_results["device_results"][device_id] = {
                        "success": False,
                        "message": "Pattern not detected in frame",
                    }

                capture_results["total_frames"][device_id] = self.capture_count[
                    device_id
                ]

            return capture_results

        except Exception as e:
            capture_results["success"] = False
            capture_results["message"] = f"Capture failed: {str(e)}"
            return capture_results

        finally:
            self.is_capturing = False

    def _simulate_image_capture(self, device_id: str) -> bool:
        """
        Simulate image capture for testing purposes.
        In real implementation, this would handle actual image data from devices.

        Args:
            device_id (str): Device identifier

        Returns:
            bool: True if capture successful
        """
        # Create dummy image data for testing
        rgb_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        thermal_image = np.random.randint(0, 255, (240, 320), dtype=np.uint8)

        # Store images (in real implementation, these would be actual captured images)
        self.captured_images[device_id]["rgb"].append(rgb_image)
        self.captured_images[device_id]["thermal"].append(thermal_image)

        # Save images to disk
        session_folder = Path(self.current_session["session_folder"])
        device_folder = session_folder / device_id
        device_folder.mkdir(exist_ok=True)

        frame_num = self.capture_count[device_id]
        rgb_path = device_folder / f"rgb_{frame_num:03d}.png"
        thermal_path = device_folder / f"thermal_{frame_num:03d}.png"

        cv2.imwrite(str(rgb_path), rgb_image)
        cv2.imwrite(str(thermal_path), thermal_image)

        print(f"[DEBUG_LOG] Simulated capture for {device_id}: frame {frame_num}")
        return True

    def can_compute_calibration(self, device_id: str = None) -> Dict[str, bool]:
        """
        Check if calibration can be computed for devices.

        Args:
            device_id (str, optional): Specific device to check, or None for all

        Returns:
            Dict: Device readiness status
        """
        if not self.current_session:
            return {}

        devices_to_check = (
            [device_id] if device_id else self.current_session["device_ids"]
        )
        readiness = {}

        for dev_id in devices_to_check:
            frame_count = self.capture_count.get(dev_id, 0)
            readiness[dev_id] = frame_count >= self.min_images

        return readiness

    def compute_calibration(self, device_id: str = None) -> Dict[str, Any]:
        """
        Compute calibration parameters for specified device(s).

        Args:
            device_id (str, optional): Specific device to calibrate, or None for all

        Returns:
            Dict: Calibration computation results
        """
        if not self.current_session:
            raise RuntimeError("No active calibration session")

        devices_to_calibrate = (
            [device_id] if device_id else self.current_session["device_ids"]
        )
        computation_results = {
            "success": True,
            "message": "Calibration computed successfully",
            "device_results": {},
        }

        for dev_id in devices_to_calibrate:
            try:
                print(f"[DEBUG_LOG] Computing calibration for device {dev_id}")

                # Check if enough images are available
                if not self.can_compute_calibration(dev_id)[dev_id]:
                    computation_results["device_results"][dev_id] = {
                        "success": False,
                        "message": f"Insufficient images: {self.capture_count[dev_id]}/{self.min_images}",
                    }
                    continue

                # Get captured images
                rgb_images = self.captured_images[dev_id]["rgb"]
                thermal_images = self.captured_images[dev_id]["thermal"]

                # Perform calibration computation
                result = self._compute_device_calibration(
                    dev_id, rgb_images, thermal_images
                )

                if result.is_valid():
                    # Store calibration result
                    self.calibration_results[dev_id] = result

                    # Save calibration data
                    self._save_calibration_result(dev_id, result)

                    computation_results["device_results"][dev_id] = {
                        "success": True,
                        "message": "Calibration computed successfully",
                        "rgb_error": result.rgb_rms_error,
                        "thermal_error": result.thermal_rms_error,
                        "stereo_error": result.stereo_rms_error,
                        "quality_score": result.quality_assessment.get(
                            "quality_score", "UNKNOWN"
                        ),
                    }
                else:
                    computation_results["device_results"][dev_id] = {
                        "success": False,
                        "message": "Calibration computation failed",
                    }

            except Exception as e:
                computation_results["device_results"][dev_id] = {
                    "success": False,
                    "message": f"Calibration error: {str(e)}",
                }
                print(f"[DEBUG_LOG] Calibration error for {dev_id}: {e}")

        # Check overall success
        all_successful = all(
            result.get("success", False)
            for result in computation_results["device_results"].values()
        )

        if not all_successful:
            computation_results["success"] = False
            computation_results["message"] = "Some device calibrations failed"

        return computation_results

    def _compute_device_calibration(
        self,
        device_id: str,
        rgb_images: List[np.ndarray],
        thermal_images: List[np.ndarray],
    ) -> CalibrationResult:
        """
        Compute calibration for a single device.

        Args:
            device_id (str): Device identifier
            rgb_images (List[np.ndarray]): RGB calibration images
            thermal_images (List[np.ndarray]): Thermal calibration images

        Returns:
            CalibrationResult: Computed calibration parameters
        """
        print(f"[DEBUG_LOG] Computing calibration for device {device_id}")

        # Create calibration result object
        result = CalibrationResult(device_id)

        # Generate object points for calibration pattern
        object_points = self.processor.create_object_points(
            self.chessboard_size, self.square_size
        )

        # Detect calibration patterns in all images
        rgb_image_points = []
        thermal_image_points = []
        valid_object_points = []

        for i, (rgb_img, thermal_img) in enumerate(zip(rgb_images, thermal_images)):
            # Detect pattern in RGB image
            rgb_success, rgb_corners = self.processor.detect_chessboard_corners(
                rgb_img, self.chessboard_size
            )

            # Detect pattern in thermal image
            thermal_success, thermal_corners = self.processor.detect_chessboard_corners(
                thermal_img, self.chessboard_size
            )

            # Only use frames where both cameras detected the pattern
            if rgb_success and thermal_success:
                rgb_image_points.append(rgb_corners)
                thermal_image_points.append(thermal_corners)
                valid_object_points.append(object_points)
                print(f"[DEBUG_LOG] Pattern detected in frame {i} for both cameras")
            else:
                print(f"[DEBUG_LOG] Pattern detection failed in frame {i}")

        if len(valid_object_points) < self.min_images:
            print(
                f"[DEBUG_LOG] Insufficient valid frames: {len(valid_object_points)}/{self.min_images}"
            )
            return result

        # Calibrate RGB camera
        rgb_image_size = (rgb_images[0].shape[1], rgb_images[0].shape[0])
        rgb_ret, rgb_camera_matrix, rgb_dist_coeffs, _, _ = cv2.calibrateCamera(
            valid_object_points, rgb_image_points, rgb_image_size, None, None
        )

        if rgb_ret:
            result.rgb_camera_matrix = rgb_camera_matrix
            result.rgb_distortion_coeffs = rgb_dist_coeffs
            result.rgb_rms_error = rgb_ret
            print(f"[DEBUG_LOG] RGB camera calibrated with RMS error: {rgb_ret:.3f}")

        # Calibrate thermal camera
        thermal_image_size = (thermal_images[0].shape[1], thermal_images[0].shape[0])
        thermal_ret, thermal_camera_matrix, thermal_dist_coeffs, _, _ = (
            cv2.calibrateCamera(
                valid_object_points,
                thermal_image_points,
                thermal_image_size,
                None,
                None,
            )
        )

        if thermal_ret:
            result.thermal_camera_matrix = thermal_camera_matrix
            result.thermal_distortion_coeffs = thermal_dist_coeffs
            result.thermal_rms_error = thermal_ret
            print(
                f"[DEBUG_LOG] Thermal camera calibrated with RMS error: {thermal_ret:.3f}"
            )

        # Perform stereo calibration if both individual calibrations succeeded
        if rgb_ret and thermal_ret:
            stereo_ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
                valid_object_points,
                rgb_image_points,
                thermal_image_points,
                rgb_camera_matrix,
                rgb_dist_coeffs,
                thermal_camera_matrix,
                thermal_dist_coeffs,
                rgb_image_size,
                flags=cv2.CALIB_FIX_INTRINSIC,
            )

            if stereo_ret:
                result.rotation_matrix = R
                result.translation_vector = T
                result.essential_matrix = E
                result.fundamental_matrix = F
                result.stereo_rms_error = stereo_ret
                print(
                    f"[DEBUG_LOG] Stereo calibration completed with RMS error: {stereo_ret:.3f}"
                )

                # Compute homography for overlay
                result.homography_matrix = self.processor.compute_homography(
                    thermal_image_points[0], rgb_image_points[0]
                )

        # Assess calibration quality
        result.quality_assessment = self._assess_calibration_quality(result)
        result.calibration_timestamp = datetime.now().isoformat()

        return result

    def _assess_calibration_quality(self, result: CalibrationResult) -> Dict[str, Any]:
        """
        Assess the quality of calibration results.

        Args:
            result (CalibrationResult): Calibration result to assess

        Returns:
            Dict: Quality assessment metrics
        """
        assessment = {"quality_score": "UNKNOWN", "recommendations": []}

        # Assess based on RMS errors
        rgb_error = result.rgb_rms_error or float("inf")
        thermal_error = result.thermal_rms_error or float("inf")
        stereo_error = result.stereo_rms_error or float("inf")

        max_error = max(rgb_error, thermal_error, stereo_error)

        if max_error < 0.5:
            assessment["quality_score"] = "EXCELLENT"
        elif max_error < 1.0:
            assessment["quality_score"] = "GOOD"
        elif max_error < 2.0:
            assessment["quality_score"] = "ACCEPTABLE"
            assessment["recommendations"].append(
                "Consider recapturing some images for better accuracy"
            )
        else:
            assessment["quality_score"] = "POOR"
            assessment["recommendations"].extend(
                [
                    "Recapture calibration images",
                    "Ensure calibration pattern is clearly visible",
                    "Use better lighting conditions",
                ]
            )

        assessment["rgb_error"] = rgb_error
        assessment["thermal_error"] = thermal_error
        assessment["stereo_error"] = stereo_error

        return assessment

    def _save_calibration_result(self, device_id: str, result: CalibrationResult):
        """
        Save calibration result to file.

        Args:
            device_id (str): Device identifier
            result (CalibrationResult): Calibration result to save
        """
        session_folder = Path(self.current_session["session_folder"])
        calibration_file = session_folder / f"calibration_{device_id}.json"

        result.save_to_file(str(calibration_file))
        print(f"[DEBUG_LOG] Calibration result saved: {calibration_file}")

    def get_calibration_result(self, device_id: str) -> Optional[CalibrationResult]:
        """
        Get calibration result for a device.

        Args:
            device_id (str): Device identifier

        Returns:
            CalibrationResult: Calibration result or None if not available
        """
        return self.calibration_results.get(device_id)

    def load_calibration_result(self, device_id: str, calibration_file: str) -> bool:
        """
        Load calibration result from file.

        Args:
            device_id (str): Device identifier
            calibration_file (str): Path to calibration file

        Returns:
            bool: True if loaded successfully
        """
        try:
            result = CalibrationResult.load_from_file(calibration_file)
            if result:
                self.calibration_results[device_id] = result
                print(f"[DEBUG_LOG] Calibration result loaded for {device_id}")
                return True
        except Exception as e:
            print(f"[DEBUG_LOG] Failed to load calibration for {device_id}: {e}")

        return False

    def apply_thermal_overlay(
        self,
        device_id: str,
        rgb_image: np.ndarray,
        thermal_image: np.ndarray,
        alpha: float = 0.3,
    ) -> Optional[np.ndarray]:
        """
        Apply thermal overlay on RGB image using calibration data.

        Args:
            device_id (str): Device identifier
            rgb_image (np.ndarray): RGB image
            thermal_image (np.ndarray): Thermal image
            alpha (float): Overlay transparency (0.0 to 1.0)

        Returns:
            np.ndarray: Overlaid image or None if calibration not available
        """
        result = self.calibration_results.get(device_id)
        if not result or result.homography_matrix is None:
            return None

        try:
            # Warp thermal image to RGB coordinate system
            thermal_warped = cv2.warpPerspective(
                thermal_image,
                result.homography_matrix,
                (rgb_image.shape[1], rgb_image.shape[0]),
            )

            # Convert thermal to color map
            thermal_colored = cv2.applyColorMap(thermal_warped, cv2.COLORMAP_JET)

            # Blend images
            overlay = cv2.addWeighted(rgb_image, 1.0 - alpha, thermal_colored, alpha, 0)

            return overlay

        except Exception as e:
            print(f"[DEBUG_LOG] Overlay error for {device_id}: {e}")
            return None

    def end_calibration_session(self) -> Dict[str, Any]:
        """
        End the current calibration session.

        Returns:
            Dict: Session summary
        """
        if not self.current_session:
            return {"success": False, "message": "No active session"}

        # Update session info
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["status"] = "completed"
        self.current_session["total_captures"] = dict(self.capture_count)
        self.current_session["calibrated_devices"] = list(
            self.calibration_results.keys()
        )

        # Save final session info
        session_folder = Path(self.current_session["session_folder"])
        session_file = session_folder / "session_info.json"
        with open(session_file, "w") as f:
            json.dump(self.current_session, f, indent=2)

        session_summary = {
            "success": True,
            "session_name": self.current_session["session_name"],
            "total_captures": dict(self.capture_count),
            "calibrated_devices": list(self.calibration_results.keys()),
            "session_folder": str(session_folder),
        }

        # Reset session state
        self.current_session = None
        self.captured_images.clear()
        self.capture_count.clear()
        self.is_capturing = False

        print(f"[DEBUG_LOG] Calibration session ended: {session_summary}")
        return session_summary

    def get_session_status(self) -> Dict[str, Any]:
        """
        Get current calibration session status.

        Returns:
            Dict: Session status information
        """
        if not self.current_session:
            return {"active": False}

        return {
            "active": True,
            "session_name": self.current_session["session_name"],
            "device_ids": self.current_session["device_ids"],
            "capture_counts": dict(self.capture_count),
            "can_compute": self.can_compute_calibration(),
            "calibrated_devices": list(self.calibration_results.keys()),
            "is_capturing": self.is_capturing,
        }


if __name__ == "__main__":
    # Test calibration manager
    print("[DEBUG_LOG] Testing CalibrationManager...")

    manager = CalibrationManager("test_calibration")

    # Start session
    session = manager.start_calibration_session(
        ["device_1", "device_2"], "test_session"
    )
    print(f"Started session: {session['session_name']}")

    # Simulate captures
    for i in range(12):
        results = manager.capture_calibration_frame(None)  # Mock device server
        print(f"Capture {i+1}: {results['total_frames']}")

    # Compute calibration
    calibration_results = manager.compute_calibration()
    print(f"Calibration results: {calibration_results}")

    # End session
    summary = manager.end_calibration_session()
    print(f"Session ended: {summary}")

    print("[DEBUG_LOG] CalibrationManager test completed")
