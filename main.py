import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
import os
import urllib.request
import sys

# Get the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else os.getcwd()

class HandGestureMouseControl:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Gesture Mouse Control")
        self.root.geometry("800x600")
        
        # MediaPipe setup using new tasks API
        # Download model if not exists
        model_path = self.download_model_if_needed()
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,  # Detect both hands
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hand_landmarker = vision.HandLandmarker.create_from_options(options)
        
        # Hand connections for drawing
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20)  # Pinky
        ]
        
        # Camera setup
        self.cap = None
        self.is_running = False
        self.is_control_active = False
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Calibration
        self.calibration_frame = None
        self.calibration_active = False
        
        # Control parameters
        self.smoothing_factor = 0.85  # Higher value = more smoothing (0.85 = 85% of previous position)
        self.last_x, self.last_y = 0, 0
        self.movement_threshold = 3  # Minimum pixels to move before updating (reduces jitter)
        self.raw_x, self.raw_y = 0, 0  # Track raw (unsmoothed) position
        self.stationary_threshold = 2  # Pixels - if raw movement is less than this, consider hand stationary
        
        
        # Create GUI
        self.create_gui()
        
        # Disable PyAutoGUI failsafe for smoother control
        pyautogui.FAILSAFE = False
    
    def download_model_if_needed(self):
        """Download the hand landmarker model if it doesn't exist"""
        # Use the script directory
        model_dir = os.path.join(SCRIPT_DIR, "models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "hand_landmarker.task")
        
        if not os.path.exists(model_path):
            print("Downloading hand landmarker model (this may take a moment)...")
            model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            try:
                urllib.request.urlretrieve(model_url, model_path)
                print("Model downloaded successfully!")
            except Exception as e:
                print(f"Error downloading model: {e}")
                print("Please download the model manually from:")
                print("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
                print(f"Save it to: {model_path}")
                raise
        
        return model_path
        
    def create_gui(self):
        # Control frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Start/Stop camera button
        self.camera_btn = ttk.Button(
            control_frame, 
            text="Start Camera", 
            command=self.toggle_camera
        )
        self.camera_btn.pack(side=tk.LEFT, padx=5)
        
        # Toggle control button
        self.control_btn = ttk.Button(
            control_frame,
            text="Enable Mouse Control",
            command=self.toggle_control,
            state=tk.DISABLED
        )
        self.control_btn.pack(side=tk.LEFT, padx=5)
        
        # Calibration button
        self.calib_btn = ttk.Button(
            control_frame,
            text="Calibrate",
            command=self.start_calibration,
            state=tk.DISABLED
        )
        self.calib_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="Status: Camera Off",
            foreground="red"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Video frame
        self.video_frame = ttk.Frame(self.root)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video label
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()
        
        # Instructions
        instructions = """
        Instructions:
        - Start Camera: Begin video feed
        - Enable Mouse Control: Activate gesture control
        - Calibrate: Set hand position range (optional)
        
        Gestures:
        - Right Hand Pointing: Move mouse cursor
        - Left Hand Pointing: Detected (no action)
        """
        self.instructions_label = ttk.Label(
            self.root,
            text=instructions,
            justify=tk.LEFT,
            font=("Arial", 9)
        )
        self.instructions_label.pack(pady=10)
        
    def toggle_camera(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.status_label.config(text="Status: Camera Error", foreground="red")
                return
            self.is_running = True
            self.camera_btn.config(text="Stop Camera")
            self.control_btn.config(state=tk.NORMAL)
            self.calib_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Camera On", foreground="green")
            self.update_frame()
        else:
            self.is_running = False
            self.is_control_active = False
            if self.cap:
                self.cap.release()
            self.camera_btn.config(text="Start Camera")
            self.control_btn.config(text="Enable Mouse Control", state=tk.DISABLED)
            self.calib_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Camera Off", foreground="red")
            self.video_label.config(image='')
            
    def toggle_control(self):
        self.is_control_active = not self.is_control_active
        if self.is_control_active:
            self.control_btn.config(text="Disable Mouse Control")
            self.status_label.config(text="Status: Mouse Control Active", foreground="blue")
        else:
            self.control_btn.config(text="Enable Mouse Control")
            self.status_label.config(text="Status: Camera On", foreground="green")
            
    def start_calibration(self):
        self.calibration_active = True
        self.calibration_frame = None
        self.status_label.config(text="Status: Calibrating - Move hand around", foreground="orange")
        
    def is_pointing(self, landmarks):
        """Check if only index finger is extended (pointing gesture)"""
        # Index finger should be extended
        if landmarks[8].y > landmarks[6].y:  # Index tip below PIP (closed)
            return False
        
        # Other fingers should be closed
        finger_tips = [12, 16, 20]  # Middle, Ring, Pinky
        finger_pips = [10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y < landmarks[pip].y:  # Tip is above PIP (extended)
                return False
        
        # Thumb can be in any position for pointing
        return True
    
    def process_hand_gestures(self, landmarks, handedness, frame_width, frame_height):
        """Process hand landmarks and control mouse based on hand type"""
        if not self.is_control_active:
            return
        
        # Determine if this is left or right hand
        # MediaPipe returns handedness as a list with category_name
        is_left_hand = False
        is_right_hand = False
        
        if handedness and len(handedness) > 0:
            # Handedness is a list of ClassificationResult objects
            category_name = handedness[0].category_name if hasattr(handedness[0], 'category_name') else str(handedness[0])
            if 'Left' in category_name or 'left' in str(category_name).lower():
                is_left_hand = True
            elif 'Right' in category_name or 'right' in str(category_name).lower():
                is_right_hand = True
        
        # If we can't determine, use hand position as fallback
        # Left hand typically has wrist on the left side of the frame
        if not is_left_hand and not is_right_hand:
            wrist_x = landmarks[0].x if len(landmarks) > 0 else 0.5
            is_left_hand = wrist_x < 0.5  # Left side of frame
            is_right_hand = not is_left_hand
        
        try:
            # RIGHT HAND GESTURES
            if is_right_hand:
                # Right hand pointing - Move mouse cursor
                if self.is_pointing(landmarks):
                    index_tip = landmarks[8]
                    # Flip x coordinate to match mirrored display
                    x = int((1.0 - index_tip.x) * self.screen_width)
                    y = int(index_tip.y * self.screen_height)
                    
                    # Clamp to screen bounds
                    x = max(0, min(self.screen_width - 1, x))
                    y = max(0, min(self.screen_height - 1, y))
                    
                    # Initialize positions if first time
                    if self.last_x == 0 and self.last_y == 0:
                        self.last_x, self.last_y = x, y
                        self.raw_x, self.raw_y = x, y
                    
                    # Calculate raw movement (how much the hand actually moved)
                    raw_dx = abs(x - self.raw_x)
                    raw_dy = abs(y - self.raw_y)
                    
                    # Check if hand is stationary (very small movement)
                    is_stationary = raw_dx < self.stationary_threshold and raw_dy < self.stationary_threshold
                    
                    if is_stationary:
                        # Hand is stationary - stop mouse movement immediately
                        # Don't apply smoothing, just keep mouse at current position
                        self.raw_x, self.raw_y = x, y
                        # Don't update last_x, last_y to prevent sliding
                    else:
                        # Hand is moving - apply smoothing
                        # Update raw position
                        self.raw_x, self.raw_y = x, y
                        
                        # Apply exponential smoothing (higher factor = more smoothing)
                        smooth_x = int(self.last_x * self.smoothing_factor + x * (1 - self.smoothing_factor))
                        smooth_y = int(self.last_y * self.smoothing_factor + y * (1 - self.smoothing_factor))
                        
                        # Calculate movement distance from last mouse position
                        dx = abs(smooth_x - self.last_x)
                        dy = abs(smooth_y - self.last_y)
                        
                        # Only move if movement exceeds threshold (reduces jitter)
                        if dx > self.movement_threshold or dy > self.movement_threshold:
                            # Move mouse with slight duration for smoother motion
                            pyautogui.moveTo(smooth_x, smooth_y, duration=0.02)
                            self.last_x, self.last_y = smooth_x, smooth_y
                        else:
                            # Movement too small, but update last position for next frame
                            self.last_x, self.last_y = smooth_x, smooth_y
            
            # LEFT HAND GESTURES
            elif is_left_hand:
                # Left hand pointing - Gesture detected (no action for now)
                if self.is_pointing(landmarks):
                    # Left hand pointing gesture is detected but has no action assigned
                    pass
        except Exception as e:
            print(f"Error in process_hand_gestures: {e}")
    
    def update_frame(self):
        if not self.is_running:
            return
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                return
            
            # Process original frame with MediaPipe (don't flip for detection)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            
            # Process with MediaPipe (on original, unflipped frame)
            detection_result = self.hand_landmarker.detect(mp_image)
            
            # Flip frame horizontally for mirror effect (only for display)
            frame = cv2.flip(frame, 1)
            
            # Draw hand landmarks and process gestures
            if detection_result.hand_landmarks:
                for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
                    # Get handedness for this hand
                    handedness = []
                    if detection_result.handedness and idx < len(detection_result.handedness):
                        handedness = detection_result.handedness[idx]
                    
                    # Determine hand type for display
                    is_left_hand = False
                    is_right_hand = False
                    hand_label = "Unknown"
                    
                    if handedness and len(handedness) > 0:
                        category_name = handedness[0].category_name if hasattr(handedness[0], 'category_name') else str(handedness[0])
                        if 'Left' in category_name or 'left' in str(category_name).lower():
                            is_left_hand = True
                            hand_label = "Left"
                        elif 'Right' in category_name or 'right' in str(category_name).lower():
                            is_right_hand = True
                            hand_label = "Right"
                    
                    # Fallback to position-based detection
                    if not is_left_hand and not is_right_hand:
                        wrist_x = hand_landmarks[0].x if len(hand_landmarks) > 0 else 0.5
                        is_left_hand = wrist_x < 0.5
                        is_right_hand = not is_left_hand
                        hand_label = "Left" if is_left_hand else "Right"
                    
                    # Choose color based on hand type
                    hand_color = (255, 0, 0) if is_left_hand else (0, 255, 0)  # Blue for left, Green for right
                    
                    # Draw landmarks using OpenCV
                    # Flip x coordinates since frame is flipped for display
                    frame_width = frame.shape[1]
                    for landmark in hand_landmarks:
                        x = int((1.0 - landmark.x) * frame_width)  # Flip x coordinate
                        y = int(landmark.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 5, hand_color, -1)
                    
                    # Draw connections
                    for connection in self.HAND_CONNECTIONS:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        if start_idx < len(hand_landmarks) and end_idx < len(hand_landmarks):
                            start_point = hand_landmarks[start_idx]
                            end_point = hand_landmarks[end_idx]
                            start_x = int((1.0 - start_point.x) * frame_width)  # Flip x coordinate
                            start_y = int(start_point.y * frame.shape[0])
                            end_x = int((1.0 - end_point.x) * frame_width)  # Flip x coordinate
                            end_y = int(end_point.y * frame.shape[0])
                            cv2.line(frame, (start_x, start_y), (end_x, end_y), hand_color, 2)
                    
                    # Process gestures if control is active
                    if self.is_control_active:
                        self.process_hand_gestures(hand_landmarks, handedness, frame.shape[1], frame.shape[0])
                    
                    # Draw gesture indicators
                    try:
                        gesture_text = ""
                        text_y = 30 + (idx * 30)  # Offset for multiple hands
                        
                        if is_right_hand:
                            if self.is_pointing(hand_landmarks):
                                gesture_text = f"{hand_label} Hand: POINTING - Mouse Move"
                            else:
                                gesture_text = f"{hand_label} Hand: Other Gesture"
                        elif is_left_hand:
                            if self.is_pointing(hand_landmarks):
                                gesture_text = f"{hand_label} Hand: POINTING - Detected"
                            else:
                                gesture_text = f"{hand_label} Hand: Other Gesture"
                        
                        if gesture_text:
                            cv2.putText(frame, gesture_text, (10, text_y), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, hand_color, 2)
                    except Exception as e:
                        print(f"Error drawing gesture indicator: {e}")
            
            # Convert to PhotoImage
            frame_pil = Image.fromarray(frame)
            frame_tk = ImageTk.PhotoImage(image=frame_pil)
            
            # Update label
            self.video_label.config(image=frame_tk)
            self.video_label.image = frame_tk  # Keep a reference
        except Exception as e:
            print(f"Error updating frame: {e}")
            return
        
        # Schedule next update
        self.root.after(10, self.update_frame)
    
    def __del__(self):
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    app = HandGestureMouseControl(root)
    root.mainloop()

if __name__ == "__main__":
    main()
