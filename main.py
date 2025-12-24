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
            num_hands=1,
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
        self.smoothing_factor = 0.7
        self.last_x, self.last_y = 0, 0
        
        # Click detection
        self.click_threshold = 0.03  # Distance threshold for click (thumb to index finger)
        self.last_click_time = 0
        self.click_cooldown = 0.5  # seconds between clicks
        
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
        - Point with index finger: Move mouse
        - Pinch thumb and index finger: Left click
        - Show 5 fingers: Right click
        - Make a fist: Middle click
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
        
    def calculate_distance(self, point1, point2):
        """Calculate 3D distance between two points"""
        dx = point1.x - point2.x
        dy = point1.y - point2.y
        dz = point1.z - point2.z if hasattr(point1, 'z') and hasattr(point2, 'z') else 0
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def is_pinch(self, landmarks):
        """Check if thumb and index finger are pinched together"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = self.calculate_distance(thumb_tip, index_tip)
        return distance < self.click_threshold
    
    def is_fist(self, landmarks):
        """Check if all fingers are closed (fist)"""
        # Check if fingertips are below their respective PIP joints
        # Thumb is checked differently (compare with thumb IP joint)
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_pips = [6, 10, 14, 18]
        
        # Check fingers (excluding thumb)
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y < landmarks[pip].y:  # Tip is above PIP (finger extended)
                return False
        
        # Check thumb separately (thumb moves differently)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        if thumb_tip.x > thumb_ip.x:  # Thumb is extended to the right
            return False
            
        return True
    
    def is_all_fingers_extended(self, landmarks):
        """Check if all fingers are extended"""
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y > landmarks[pip].y:  # Tip is below PIP (finger closed)
                return False
        return True
    
    def process_hand_gestures(self, landmarks, frame_width, frame_height):
        """Process hand landmarks and control mouse"""
        if not self.is_control_active:
            return
        
        try:
            # Get index finger tip position
            index_tip = landmarks[8]
            
            # Convert normalized coordinates to screen coordinates
            x = int(index_tip.x * self.screen_width)
            y = int(index_tip.y * self.screen_height)
            
            # Clamp to screen bounds
            x = max(0, min(self.screen_width - 1, x))
            y = max(0, min(self.screen_height - 1, y))
            
            # Smooth mouse movement
            if self.last_x == 0 and self.last_y == 0:
                self.last_x, self.last_y = x, y
            
            smooth_x = int(self.last_x * (1 - self.smoothing_factor) + x * self.smoothing_factor)
            smooth_y = int(self.last_y * (1 - self.smoothing_factor) + y * self.smoothing_factor)
            
            # Move mouse
            pyautogui.moveTo(smooth_x, smooth_y, duration=0.01)
            self.last_x, self.last_y = smooth_x, smooth_y
        except Exception as e:
            print(f"Error in process_hand_gestures: {e}")
        
        # Detect gestures for clicking
        current_time = time.time()
        
        # Left click (pinch)
        if self.is_pinch(landmarks):
            if current_time - self.last_click_time > self.click_cooldown:
                pyautogui.click()
                self.last_click_time = current_time
                
        # Right click (all fingers extended)
        elif self.is_all_fingers_extended(landmarks):
            if current_time - self.last_click_time > self.click_cooldown:
                pyautogui.rightClick()
                self.last_click_time = current_time
                
        # Middle click (fist)
        elif self.is_fist(landmarks):
            if current_time - self.last_click_time > self.click_cooldown:
                pyautogui.middleClick()
                self.last_click_time = current_time
    
    def update_frame(self):
        if not self.is_running:
            return
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                return
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            
            # Process with MediaPipe
            detection_result = self.hand_landmarker.detect(mp_image)
            
            # Draw hand landmarks
            if detection_result.hand_landmarks:
                for hand_landmarks in detection_result.hand_landmarks:
                    # Convert to landmark list for drawing
                    landmarks_list = []
                    for landmark in hand_landmarks:
                        landmarks_list.append([landmark.x, landmark.y, landmark.z])
                    
                    # Draw landmarks using OpenCV
                    for idx, landmark in enumerate(hand_landmarks):
                        x = int(landmark.x * frame.shape[1])
                        y = int(landmark.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                    
                    # Draw connections
                    for connection in self.HAND_CONNECTIONS:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        start_point = hand_landmarks[start_idx]
                        end_point = hand_landmarks[end_idx]
                        start_x = int(start_point.x * frame.shape[1])
                        start_y = int(start_point.y * frame.shape[0])
                        end_x = int(end_point.x * frame.shape[1])
                        end_y = int(end_point.y * frame.shape[0])
                        cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
                    
                    # Process gestures if control is active
                    if self.is_control_active:
                        self.process_hand_gestures(hand_landmarks, frame.shape[1], frame.shape[0])
                        
                    # Draw gesture indicators
                    try:
                        if self.is_pinch(hand_landmarks):
                            cv2.putText(frame, "PINCH - Left Click", (10, 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        elif self.is_all_fingers_extended(hand_landmarks):
                            cv2.putText(frame, "OPEN HAND - Right Click", (10, 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        elif self.is_fist(hand_landmarks):
                            cv2.putText(frame, "FIST - Middle Click", (10, 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        else:
                            cv2.putText(frame, "POINTING - Mouse Move", (10, 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
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
