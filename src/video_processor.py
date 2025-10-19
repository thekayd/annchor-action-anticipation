"""
Video Processing Module for I3D Feature Extraction
Extracts I3D features from uploaded ballet videos
"""

import numpy as np
import cv2
import tempfile
import os
from pathlib import Path
from typing import Tuple, Optional

class VideoProcessor:
    # this class processes uploaded videos and extracts I3D-like features
    
    def __init__(self, target_frames: int = 10, feature_dim: int = 2048):
        # this function initializes the video processor with target frames which is 10 and is the number of frames to extract and feature dimensions which is 2048 
        self.target_frames = target_frames
        self.feature_dim = feature_dim
    
    def extract_features_from_video_segment(self, video_path: str, start_time: float = 0, duration: float = 10) -> np.ndarray:
        # this function extracts I3D-like features from a specific segment of video
        # it takes in the video path of the file, start time which is 0 by default in seconds and duration which is 10
        try:
            # opens the video file
            video = cv2.VideoCapture(video_path)
            
            if not video.isOpened():
                raise ValueError("Could not open video file")
            
            # gets video information
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # calculates which frames we want to look at
            start_frame = int(start_time * fps)
            end_frame = int((start_time + duration) * fps)
            
            # makes sure we don't go past the end of the video
            if end_frame > total_frames:
                end_frame = total_frames
            
            # counts how many frames are in this segment
            frames_in_segment = end_frame - start_frame
            
            # if there are no frames, this then returns empty features
            if frames_in_segment <= 0:
                video.release()
                empty_features = np.zeros((self.target_frames, self.feature_dim), dtype=np.float32)
                return empty_features
            
            # this decides which frames to use (spread them out evenly)
            if frames_in_segment <= self.target_frames:
                frame_numbers = list(range(start_frame, end_frame))
            else:
                frame_numbers = np.linspace(start_frame, end_frame - 1, self.target_frames, dtype=int)
            
            # gets the actual frames from the video
            frames = []
            for frame_number in frame_numbers:
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                success, frame = video.read()
                
                if success:
                    # this cleans up the frame
                    clean_frame = self._preprocess_frame(frame)
                    frames.append(clean_frame)
            
            # closes the video file
            video.release()
            
            # this generates features from frames
            features = self._generate_features_from_frames(frames)
            
            return features
            
        except Exception as e:
            raise Exception(f"Error extracting features: {str(e)}")
    
    def extract_features_from_video(self, video_path: str) -> np.ndarray:
        # this function extracts I3D-like features from the entire video file by opening the video file and getting the total frames and fps and then sampling frames uniformly and extracting frames and generating features from frames
        # it takes in the video path of the file and returns a numpy array of shape (target_frames, feature_dim)
        try:
            # opens the video file
            video = cv2.VideoCapture(video_path)
            
            if not video.isOpened():
                raise ValueError("Could not open video file")
            
            # gets information about the video
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video.get(cv2.CAP_PROP_FPS)
            
            print(f"Video info: {total_frames} frames, {fps} fps")
            
            # this decides which frames to use from the whole video
            frame_numbers = self._get_frame_indices(total_frames)
            
            # this gets the actual frames from the video
            frames = []
            for frame_number in frame_numbers:
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                success, frame = video.read()
                
                if success:
                    # this cleans up the frame
                    clean_frame = self._preprocess_frame(frame)
                    frames.append(clean_frame)
            
            # this closes the video file
            video.release()
            
            # this generates I3D-like features
            # In a real implementation, you would use a pre-trained I3D model here
            # For now, this generates features from frame statistics
            features = self._generate_features_from_frames(frames)
            
            return features
            
        except Exception as e:
            raise Exception(f"Error extracting features: {str(e)}")
    
    def _get_frame_indices(self, total_frames: int) -> list:
        # this function gets uniformly sampled frame indices from the video
        # it takes in the total frames of the video and returns a list of frame indices to sample
        # if the video has fewer frames than we want, this then uses all of them
        if total_frames <= self.target_frames:
            frame_numbers = list(range(total_frames))
            return frame_numbers
        
        # if the video has more frames, this then picks some evenly spaced ones
        frame_numbers = np.linspace(0, total_frames - 1, self.target_frames, dtype=int)
        return frame_numbers.tolist()
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        # this function preprocesses video frames by resizing and normalizing
        # this makes the frame smaller so it's always the same size
        small_frame = cv2.resize(frame, (224, 224))
        
        # changes the pixel values from 0-255 to 0-1
        normalized_frame = small_frame.astype(np.float32) / 255.0
        
        return normalized_frame
    
    def _generate_features_from_frames(self, frames: list) -> np.ndarray:
        # this function generates I3D-like features from frames using frame statistics
        # it takes in a list of frames and returns a numpy array of shape (target_frames, feature_dim)
        all_features = []
        
        for frame in frames:
            # this calculates some basic statistics from the frame
            # this is a simple way to create features - real I3D would use deep learning
            
            # finds the average color values
            mean_values = np.mean(frame, axis=(0, 1))
            
            # finds how much the colors vary from the mean
            std_values = np.std(frame, axis=(0, 1))
            
            # finds the brightest colors
            max_values = np.max(frame, axis=(0, 1))
            
            # find sthe darkest colors
            min_values = np.min(frame, axis=(0, 1))
            
            # this puts all these statistics together
            frame_features = np.concatenate([mean_values, std_values, max_values, min_values])
            
            # make sure the feature vector is the right size
            if len(frame_features) < self.feature_dim:
                # if it's too small, this then adds some random numbers to make it bigger
                extra_numbers = np.random.randn(self.feature_dim - len(frame_features)) * 0.1
                frame_features = np.concatenate([frame_features, extra_numbers])
            else:
                # if it's too big, this then cuts it down to size
                frame_features = frame_features[:self.feature_dim]
            
            all_features.append(frame_features)
        
        # this makes sure we have exactly the right number of frames
        while len(all_features) < self.target_frames:
            if all_features:
                # if we need more frames, this then copies the last one
                all_features.append(all_features[-1])
            else:
                # if we have no frames, this then creates empty ones
                all_features.append(np.zeros(self.feature_dim))
        
        # this only keeps the number of frames we want
        final_features = np.array(all_features[:self.target_frames], dtype=np.float32)
        
        return final_features
    
    def save_temp_video(self, video_bytes: bytes, suffix: str = '.mp4') -> str:
        # this function saves uploaded video bytes to a temporary file
        # this creates a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        # this writes the video data to the file
        temp_file.write(video_bytes)
        
        # closes the file and returns its name
        temp_file.close()
        return temp_file.name
    
    def cleanup_temp_file(self, file_path: str):
        # this function removes temporary files after processing
        try:
            # checks if the file exists
            if os.path.exists(file_path):
                # this deletes the file
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove temp file {file_path}: {e}")

