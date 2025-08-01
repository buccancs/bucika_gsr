"""
Hand Segmentation Engine - Main processing orchestrator.

This module contains the main HandSegmentationEngine class that orchestrates
hand segmentation processing using different algorithms and handles video I/O.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import os
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import cv2
import numpy as np

from .utils import (
    SegmentationConfig, SegmentationMethod, HandRegion, ProcessingResult,
    crop_frame_to_region, resize_frame, save_processing_metadata
)
from .models import (
    BaseHandSegmentation, MediaPipeHandSegmentation,
    ColorBasedHandSegmentation, ContourBasedHandSegmentation
)


class HandSegmentationEngine:
    """
    Main engine for hand segmentation processing.
    
    This class coordinates the overall hand segmentation workflow, including:
    - Video loading and processing
    - Algorithm selection and initialization
    - Output generation (masks, cropped regions, metadata)
    - Progress tracking and error handling
    """
    
    def __init__(self, config: SegmentationConfig):
        """
        Initialize the segmentation engine.
        
        Args:
            config: Segmentation configuration
        """
        self.config = config
        self.segmentation_model: Optional[BaseHandSegmentation] = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the segmentation engine with the configured algorithm.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Create segmentation model based on config
            if self.config.method == SegmentationMethod.MEDIAPIPE:
                self.segmentation_model = MediaPipeHandSegmentation(self.config)
            elif self.config.method == SegmentationMethod.COLOR_BASED:
                self.segmentation_model = ColorBasedHandSegmentation(self.config)
            elif self.config.method == SegmentationMethod.CONTOUR_BASED:
                self.segmentation_model = ContourBasedHandSegmentation(self.config)
            else:
                print(f"[ERROR] Unknown segmentation method: {self.config.method}")
                return False
            
            # Initialize the selected model
            if not self.segmentation_model.initialize():
                print(f"[ERROR] Failed to initialize {self.config.method.value} model")
                return False
            
            self.is_initialized = True
            print(f"[INFO] Hand segmentation engine initialized with {self.config.method.value}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error initializing segmentation engine: {e}")
            return False
    
    def process_video(self, input_video_path: str, output_directory: str) -> ProcessingResult:
        """
        Process a video file for hand segmentation.
        
        Args:
            input_video_path: Path to input video file
            output_directory: Directory to save output files
            
        Returns:
            ProcessingResult: Result of the processing operation
        """
        start_time = time.time()
        
        # Initialize result object
        result = ProcessingResult(
            input_video_path=input_video_path,
            output_directory=output_directory
        )
        
        if not self.is_initialized:
            result.error_message = "Segmentation engine not initialized"
            return result
        
        try:
            # Create output directory
            os.makedirs(output_directory, exist_ok=True)
            
            # Open video
            cap = cv2.VideoCapture(input_video_path)
            if not cap.isOpened():
                result.error_message = f"Could not open video: {input_video_path}"
                return result
            
            # Get video properties
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"[INFO] Processing video: {frame_width}x{frame_height} @ {fps:.1f} FPS, {total_frames} frames")
            
            # Initialize output files
            output_files = {}
            video_writers = {}
            
            # Setup cropped video output if requested
            if self.config.output_cropped:
                cropped_video_path = os.path.join(output_directory, "hands_cropped.mp4")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                # Use smaller resolution for cropped video
                crop_width, crop_height = 640, 480
                video_writers['cropped'] = cv2.VideoWriter(
                    cropped_video_path, fourcc, fps, (crop_width, crop_height)
                )
                output_files['cropped_video'] = cropped_video_path
            
            # Setup mask video output if requested
            if self.config.output_masks:
                mask_video_path = os.path.join(output_directory, "hand_masks.mp4")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writers['mask'] = cv2.VideoWriter(
                    mask_video_path, fourcc, fps, (frame_width, frame_height)
                )
                output_files['mask_video'] = mask_video_path
            
            # Process frames
            frame_count = 0
            total_detections = 0
            detection_log = []
            
            print(f"[INFO] Starting frame processing...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process frame for hand detection
                hand_regions = self.segmentation_model.process_frame(frame)
                total_detections += len(hand_regions)
                
                # Log detection info
                frame_info = {
                    'frame': frame_count,
                    'hands_detected': len(hand_regions),
                    'regions': []
                }
                
                # Process each detected hand
                for i, hand_region in enumerate(hand_regions):
                    frame_info['regions'].append({
                        'bbox': hand_region.bbox,
                        'confidence': hand_region.confidence,
                        'hand_label': hand_region.hand_label
                    })
                    
                    # Save cropped hand region if requested
                    if self.config.output_cropped and video_writers.get('cropped'):
                        cropped = crop_frame_to_region(frame, hand_region.bbox)
                        if cropped.size > 0:
                            # Resize to standard size
                            cropped_resized = resize_frame(cropped, (640, 480))
                            video_writers['cropped'].write(cropped_resized)
                
                # Create and save mask frame if requested
                if self.config.output_masks and video_writers.get('mask'):
                    combined_mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
                    for hand_region in hand_regions:
                        if hand_region.mask is not None:
                            combined_mask = cv2.bitwise_or(combined_mask, hand_region.mask)
                    
                    # Convert mask to 3-channel for video output
                    mask_colored = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)
                    video_writers['mask'].write(mask_colored)
                
                detection_log.append(frame_info)
                
                # Progress update every 100 frames
                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"[INFO] Progress: {frame_count}/{total_frames} frames ({progress:.1f}%)")
            
            # Clean up video capture and writers
            cap.release()
            for writer in video_writers.values():
                writer.release()
            
            # Save detection log
            detection_log_path = os.path.join(output_directory, "detection_log.json")
            import json
            with open(detection_log_path, 'w') as f:
                json.dump(detection_log, f, indent=2)
            output_files['detection_log'] = detection_log_path
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update result
            result.processed_frames = frame_count
            result.detected_hands_count = total_detections
            result.processing_time = processing_time
            result.output_files = output_files
            result.success = True
            
            print(f"[INFO] Processing completed: {frame_count} frames, {total_detections} detections, {processing_time:.2f}s")
            
            # Save metadata
            metadata_path = os.path.join(output_directory, "processing_metadata.json")
            save_processing_metadata(result, metadata_path)
            result.output_files['metadata'] = metadata_path
            
            return result
            
        except Exception as e:
            result.error_message = f"Error processing video: {str(e)}"
            print(f"[ERROR] {result.error_message}")
            return result
    
    def process_frame_batch(self, frames: List[np.ndarray]) -> List[List[HandRegion]]:
        """
        Process a batch of frames for hand detection.
        
        Args:
            frames: List of frames to process
            
        Returns:
            List of hand regions for each frame
        """
        if not self.is_initialized:
            return []
        
        results = []
        for frame in frames:
            hand_regions = self.segmentation_model.process_frame(frame)
            results.append(hand_regions)
        
        return results
    
    def get_supported_methods(self) -> List[str]:
        """
        Get list of supported segmentation methods.
        
        Returns:
            List of method names
        """
        return [method.value for method in SegmentationMethod]
    
    def cleanup(self):
        """Clean up resources."""
        if self.segmentation_model:
            self.segmentation_model.cleanup()
            self.segmentation_model = None
        self.is_initialized = False
        print("[INFO] Hand segmentation engine cleaned up")


def create_segmentation_engine(method: str = "mediapipe", **kwargs) -> HandSegmentationEngine:
    """
    Factory function to create a configured segmentation engine.
    
    Args:
        method: Segmentation method ("mediapipe", "color_based", "contour_based")
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured HandSegmentationEngine
    """
    # Create config with provided parameters
    config_params = {
        'method': SegmentationMethod(method),
        **kwargs
    }
    
    config = SegmentationConfig(**config_params)
    engine = HandSegmentationEngine(config)
    
    return engine