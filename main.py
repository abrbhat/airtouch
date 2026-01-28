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
import ctypes

# Get the script directory
# Handle PyInstaller bundled mode
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    SCRIPT_DIR = sys._MEIPASS
else:
    # Running as script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else os.getcwd()



class CornerIndicator:
    """Visual indicator fixed in screen corner showing gesture control status."""

    COLOR_ON = '#22c55e'   # Green
    COLOR_OFF = '#6b7280'  # Gray

    def __init__(self, parent_root, corner='bottom_right'):
        self.parent = parent_root
        self.corner = corner
        self.visible = False
        self.window = None
        self.is_on = False
        self.width = 70
        self.height = 32

    def create_window(self):
        """Create the indicator overlay window."""
        self.window = tk.Toplevel(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.95)

        # Create frame with padding for visual appeal
        self.frame = tk.Frame(self.window, bg=self.COLOR_OFF, padx=12, pady=4)
        self.frame.pack(expand=True, fill='both')

        # Add a label to show status
        self.label = tk.Label(
            self.frame,
            text="OFF",
            bg=self.COLOR_OFF,
            fg='white',
            font=('Segoe UI', 11, 'bold')
        )
        self.label.pack(expand=True)

        self.window.geometry(f'{self.width}x{self.height}')
        self._position_in_corner()

        # Start hidden
        self.window.withdraw()

    def _position_in_corner(self):
        """Position the window in the specified screen corner."""
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        margin = 15
        taskbar_height = 130  # Extra space above taskbar

        if self.corner == 'top_left':
            x, y = margin, margin
        elif self.corner == 'top_right':
            x, y = screen_width - self.width - margin, margin
        elif self.corner == 'bottom_left':
            x, y = margin, screen_height - self.height - taskbar_height
        else:  # bottom_right
            x, y = screen_width - self.width - margin, screen_height - self.height - taskbar_height

        self.window.geometry(f'{self.width}x{self.height}+{x}+{y}')

    def set_state(self, is_on):
        """Set the indicator state (ON or OFF)."""
        if not self.window:
            self.create_window()

        self.is_on = is_on
        color = self.COLOR_ON if is_on else self.COLOR_OFF
        text = "ON" if is_on else "OFF"

        self.frame.configure(bg=color)
        self.label.configure(bg=color, text=text)

    def show(self):
        """Show the indicator."""
        if not self.window:
            self.create_window()
        self.visible = True
        self.window.deiconify()
        self.window.lift()

    def hide(self):
        """Hide the indicator."""
        self.visible = False
        if self.window:
            self.window.withdraw()

    def destroy(self):
        """Clean up the indicator window."""
        self.visible = False
        if self.window:
            self.window.destroy()
            self.window = None


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
        
        # Control parameters
        self.smoothing_factor = 0.85  # Higher value = more smoothing
        self.movement_threshold = 0.001  # Minimum normalized movement (0-1 range) to trigger mouse movement
        self.sensitivity = 3.0  # Multiplier for finger movement to mouse movement (higher = more sensitive)
        self.last_finger_x = None  # Previous finger position in normalized coordinates (0-1)
        self.last_finger_y = None
        self.smoothed_dx = 0.0  # Smoothed movement delta
        self.smoothed_dy = 0.0
        
        # Click detection
        self.click_threshold = 0.03  # Distance threshold for pinch gesture (thumb to index finger)
        self.last_click_time = 0
        self.click_cooldown = 2.0  # seconds between clicks
        
        # Scroll detection
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.1  # seconds between scroll actions
        self.scroll_speed = 12  # Scroll units per gesture

        # Toggle control detection (both fists)
        self.last_toggle_time = 0
        self.toggle_cooldown = 1.5  # seconds between toggle actions

        # Corner indicator for control status
        self.cursor_indicator = CornerIndicator(self.root)

        # Create GUI
        self.create_gui()
        
        # Disable PyAutoGUI failsafe for smoother control
        pyautogui.FAILSAFE = False
    
    def download_model_if_needed(self):
        """Download the hand landmarker model if it doesn't exist"""
        # For PyInstaller, use the bundled models directory
        # For regular execution, use script directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use bundled models
            model_path = os.path.join(SCRIPT_DIR, "models", "hand_landmarker.task")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found in bundled resources: {model_path}")
        else:
            # Running as script - use script directory
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
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="Status: Camera Off",
            foreground="red"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Video Feed
        self.video_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.video_tab, text="Video Feed")
        
        # Video frame
        self.video_frame = ttk.Frame(self.video_tab)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video label
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()
        
        # Instructions
        instructions = """
        Instructions:
        - Start Camera: Begin video feed
        - Enable Mouse Control: Activate gesture control

        Gestures:
        - Both Hands Fist (apart): Toggle mouse control on/off
        - Right Hand Thumb Up: Left click
        - Right Hand Open Palm: Scroll down
        - Right Hand Victory (2 fingers): Double click
        - Right Hand Pointing: Move mouse cursor
        - Left Hand Pointing: Left click
        - Left Hand Victory: Open Task View
        - Left Hand Open Palm: Scroll up
        """
        self.instructions_label = ttk.Label(
            self.video_tab,
            text=instructions,
            justify=tk.LEFT,
            font=("Arial", 9)
        )
        self.instructions_label.pack(pady=10)
        
        # Tab 2: Settings
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        self.create_settings_tab()
    
    def create_settings_tab(self):
        """Create settings tab with adjustable parameters"""
        settings_frame = ttk.Frame(self.settings_tab, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scroll Speed
        scroll_frame = ttk.LabelFrame(settings_frame, text="Scroll Speed", padding="10")
        scroll_frame.pack(fill=tk.X, pady=10)
        
        self.scroll_speed_var = tk.DoubleVar(value=self.scroll_speed)
        scroll_speed_label = ttk.Label(scroll_frame, text="Scroll Units:")
        scroll_speed_label.pack(side=tk.LEFT, padx=5)
        
        self.scroll_speed_scale = ttk.Scale(
            scroll_frame,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.scroll_speed_var,
            command=self.update_scroll_speed
        )
        self.scroll_speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.scroll_speed_value_label = ttk.Label(scroll_frame, text=str(self.scroll_speed))
        self.scroll_speed_value_label.pack(side=tk.LEFT, padx=5)
        
        # Mouse Sensitivity
        sensitivity_frame = ttk.LabelFrame(settings_frame, text="Mouse Sensitivity", padding="10")
        sensitivity_frame.pack(fill=tk.X, pady=10)
        
        self.sensitivity_var = tk.DoubleVar(value=self.sensitivity)
        sensitivity_label = ttk.Label(sensitivity_frame, text="Sensitivity:")
        sensitivity_label.pack(side=tk.LEFT, padx=5)
        
        self.sensitivity_scale = ttk.Scale(
            sensitivity_frame,
            from_=0.5,
            to=15.0,
            orient=tk.HORIZONTAL,
            variable=self.sensitivity_var,
            command=self.update_sensitivity
        )
        self.sensitivity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.sensitivity_value_label = ttk.Label(sensitivity_frame, text=f"{self.sensitivity:.1f}")
        self.sensitivity_value_label.pack(side=tk.LEFT, padx=5)
        
        # Smoothing Factor
        smoothing_frame = ttk.LabelFrame(settings_frame, text="Mouse Smoothing", padding="10")
        smoothing_frame.pack(fill=tk.X, pady=10)
        
        self.smoothing_var = tk.DoubleVar(value=self.smoothing_factor)
        smoothing_label = ttk.Label(smoothing_frame, text="Smoothing:")
        smoothing_label.pack(side=tk.LEFT, padx=5)
        
        self.smoothing_scale = ttk.Scale(
            smoothing_frame,
            from_=0.5,
            to=0.95,
            orient=tk.HORIZONTAL,
            variable=self.smoothing_var,
            command=self.update_smoothing
        )
        self.smoothing_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.smoothing_value_label = ttk.Label(smoothing_frame, text=f"{self.smoothing_factor:.2f}")
        self.smoothing_value_label.pack(side=tk.LEFT, padx=5)
        
        # Movement Threshold
        threshold_frame = ttk.LabelFrame(settings_frame, text="Movement Threshold", padding="10")
        threshold_frame.pack(fill=tk.X, pady=10)
        
        self.threshold_var = tk.DoubleVar(value=self.movement_threshold)
        threshold_label = ttk.Label(threshold_frame, text="Threshold:")
        threshold_label.pack(side=tk.LEFT, padx=5)
        
        self.threshold_scale = ttk.Scale(
            threshold_frame,
            from_=0.0001,
            to=0.01,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            command=self.update_threshold
        )
        self.threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.threshold_value_label = ttk.Label(threshold_frame, text=f"{self.movement_threshold:.4f}")
        self.threshold_value_label.pack(side=tk.LEFT, padx=5)
        
        # Click Cooldown
        cooldown_frame = ttk.LabelFrame(settings_frame, text="Click Cooldown", padding="10")
        cooldown_frame.pack(fill=tk.X, pady=10)
        
        self.cooldown_var = tk.DoubleVar(value=self.click_cooldown)
        cooldown_label = ttk.Label(cooldown_frame, text="Cooldown (seconds):")
        cooldown_label.pack(side=tk.LEFT, padx=5)
        
        self.cooldown_scale = ttk.Scale(
            cooldown_frame,
            from_=0.1,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.cooldown_var,
            command=self.update_cooldown
        )
        self.cooldown_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.cooldown_value_label = ttk.Label(cooldown_frame, text=f"{self.click_cooldown:.2f}s")
        self.cooldown_value_label.pack(side=tk.LEFT, padx=5)
        
        # Scroll Cooldown
        scroll_cooldown_frame = ttk.LabelFrame(settings_frame, text="Scroll Cooldown", padding="10")
        scroll_cooldown_frame.pack(fill=tk.X, pady=10)
        
        self.scroll_cooldown_var = tk.DoubleVar(value=self.scroll_cooldown)
        scroll_cooldown_label = ttk.Label(scroll_cooldown_frame, text="Cooldown (seconds):")
        scroll_cooldown_label.pack(side=tk.LEFT, padx=5)
        
        self.scroll_cooldown_scale = ttk.Scale(
            scroll_cooldown_frame,
            from_=0.05,
            to=0.5,
            orient=tk.HORIZONTAL,
            variable=self.scroll_cooldown_var,
            command=self.update_scroll_cooldown
        )
        self.scroll_cooldown_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.scroll_cooldown_value_label = ttk.Label(scroll_cooldown_frame, text=f"{self.scroll_cooldown:.2f}s")
        self.scroll_cooldown_value_label.pack(side=tk.LEFT, padx=5)
    
    def update_scroll_speed(self, value=None):
        """Update scroll speed parameter"""
        self.scroll_speed = int(float(self.scroll_speed_var.get()))
        self.scroll_speed_value_label.config(text=str(self.scroll_speed))
    
    def update_sensitivity(self, value=None):
        """Update mouse sensitivity parameter"""
        self.sensitivity = float(self.sensitivity_var.get())
        self.sensitivity_value_label.config(text=f"{self.sensitivity:.1f}")
    
    def update_smoothing(self, value=None):
        """Update smoothing factor parameter"""
        self.smoothing_factor = float(self.smoothing_var.get())
        self.smoothing_value_label.config(text=f"{self.smoothing_factor:.2f}")
    
    def update_threshold(self, value=None):
        """Update movement threshold parameter"""
        self.movement_threshold = float(self.threshold_var.get())
        self.threshold_value_label.config(text=f"{self.movement_threshold:.4f}")
    
    def update_cooldown(self, value=None):
        """Update click cooldown parameter"""
        self.click_cooldown = float(self.cooldown_var.get())
        self.cooldown_value_label.config(text=f"{self.click_cooldown:.2f}s")
    
    def update_scroll_cooldown(self, value=None):
        """Update scroll cooldown parameter"""
        self.scroll_cooldown = float(self.scroll_cooldown_var.get())
        self.scroll_cooldown_value_label.config(text=f"{self.scroll_cooldown:.2f}s")
        
    def toggle_camera(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.status_label.config(text="Status: Camera Error", foreground="red")
                return
            self.is_running = True
            self.camera_btn.config(text="Stop Camera")
            self.control_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Camera On", foreground="green")
            # Show indicator in OFF state when camera starts
            self.cursor_indicator.set_state(False)
            self.cursor_indicator.show()
            self.update_frame()
        else:
            self.is_running = False
            self.is_control_active = False
            if self.cap:
                self.cap.release()
            self.camera_btn.config(text="Start Camera")
            self.control_btn.config(text="Enable Mouse Control", state=tk.DISABLED)
            self.status_label.config(text="Status: Camera Off", foreground="red")
            self.video_label.config(image='')
            # Hide indicator when camera stops
            self.cursor_indicator.hide()
            
    def toggle_control(self):
        self.is_control_active = not self.is_control_active
        if self.is_control_active:
            self.control_btn.config(text="Disable Mouse Control")
            self.status_label.config(text="Status: Mouse Control Active", foreground="blue")
            # Reset finger tracking when enabling control
            self.last_finger_x = None
            self.last_finger_y = None
            self.smoothed_dx = 0.0
            self.smoothed_dy = 0.0
            # Update indicator to ON state
            self.cursor_indicator.set_state(True)
        else:
            self.control_btn.config(text="Enable Mouse Control")
            self.status_label.config(text="Status: Camera On", foreground="green")
            # Update indicator to OFF state
            self.cursor_indicator.set_state(False)
    
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
        """Check if all fingers are closed (fist gesture)
        Uses two methods to handle different hand orientations:
        1. Y-coordinate: tip at or below PIP (works for side view)
        2. Distance: tip close to MCP (works for forward-facing fist)
        """
        # Check fingers (Index, Middle, Ring, Pinky)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        finger_mcps = [5, 9, 13, 17]

        for tip_idx, pip_idx, mcp_idx in zip(finger_tips, finger_pips, finger_mcps):
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            mcp = landmarks[mcp_idx]

            # Method 1: Y-coordinate check (tip at or below PIP)
            y_closed = tip.y >= pip.y

            # Method 2: Distance check (tip close to MCP = curled finger)
            dx = tip.x - mcp.x
            dy = tip.y - mcp.y
            dz = (tip.z - mcp.z) if hasattr(tip, 'z') else 0
            distance = (dx*dx + dy*dy + dz*dz) ** 0.5
            distance_closed = distance < 0.13

            # Finger is closed if EITHER method indicates closed
            if not (y_closed or distance_closed):
                return False

        # Check thumb separately
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]

        # Method 1: Y-check for thumb
        thumb_y_closed = thumb_tip.y >= thumb_ip.y

        # Method 2: Distance check for thumb
        dx = thumb_tip.x - thumb_mcp.x
        dy = thumb_tip.y - thumb_mcp.y
        dz = (thumb_tip.z - thumb_mcp.z) if hasattr(thumb_tip, 'z') else 0
        thumb_distance = (dx*dx + dy*dy + dz*dz) ** 0.5
        thumb_distance_closed = thumb_distance < 0.15

        if not (thumb_y_closed or thumb_distance_closed):
            return False

        return True
    
    def is_open_palm(self, landmarks):
        """Check if all fingers are extended (open palm)"""
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_pips = [6, 10, 14, 18]

        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y >= landmarks[pip].y:  # Finger not extended
                return False

        return True

    def _get_finger_curl(self, landmarks):
        """Calculate how much the fingers are curled (0.0 = straight, 1.0 = fully bent).
        Used for dynamic scroll speed - more curl = faster scroll."""
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_pips = [6, 10, 14, 18]
        finger_mcps = [5, 9, 13, 17]

        total_curl = 0.0
        for tip_idx, pip_idx, mcp_idx in zip(finger_tips, finger_pips, finger_mcps):
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            mcp = landmarks[mcp_idx]

            # Measure how close tip is to MCP relative to fully extended
            # When straight: tip is far from MCP (low curl)
            # When bent: tip is close to MCP (high curl)
            dx = tip.x - mcp.x
            dy = tip.y - mcp.y
            tip_to_mcp = (dx*dx + dy*dy) ** 0.5

            # Normalize: ~0.2 is extended, ~0.08 is bent
            # Map to 0-1 range (inverted: smaller distance = more curl)
            curl = max(0.0, min(1.0, (0.18 - tip_to_mcp) / 0.10))
            total_curl += curl

        # Average curl across 4 fingers
        return total_curl / 4.0
    
    def is_victory(self, landmarks):
        """Check if index and middle fingers are extended (victory/peace sign)"""
        # Index and middle should be extended
        if landmarks[8].y >= landmarks[6].y or landmarks[12].y >= landmarks[10].y:
            return False
        
        # Ring and pinky should be closed
        if landmarks[16].y < landmarks[14].y or landmarks[20].y < landmarks[18].y:
            return False
        
        return True
    
    def is_ok_sign(self, landmarks):
        """Check if thumb and index form a circle (OK sign)"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        thumb_ip = landmarks[3]
        index_pip = landmarks[6]
        
        # Check if thumb and index are close together (forming circle)
        distance = self.calculate_distance(thumb_tip, index_tip)
        if distance > 0.04:  # Too far apart
            return False
        
        # Other fingers should be extended
        if landmarks[12].y >= landmarks[10].y or landmarks[16].y >= landmarks[14].y or landmarks[20].y >= landmarks[18].y:
            return False
        
        return True
    
    def is_rock(self, landmarks):
        """Check if index and pinky are extended (rock/devil horns gesture)"""
        # Index and pinky should be extended
        if landmarks[8].y >= landmarks[6].y or landmarks[20].y >= landmarks[18].y:
            return False
        
        # Middle and ring should be closed
        if landmarks[12].y < landmarks[10].y or landmarks[16].y < landmarks[14].y:
            return False
        
        return True
    
    def get_gesture_name(self, landmarks):
        """Get the name of the detected gesture"""
        if self.is_thumb_up(landmarks):
            return "THUMB UP"
        elif self.is_fist(landmarks):
            return "FIST"
        elif self.is_pointing(landmarks):
            return "POINTING"
        elif self.is_pinch(landmarks):
            return "PINCH"
        elif self.is_open_palm(landmarks):
            return "OPEN PALM"
        elif self.is_victory(landmarks):
            return "VICTORY"
        elif self.is_ok_sign(landmarks):
            return "OK SIGN"
        elif self.is_rock(landmarks):
            return "ROCK"
        else:
            return "UNKNOWN"
        
    def is_thumb_up(self, landmarks):
        """Check if thumb is extended upward (thumb up gesture)"""
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]  # Thumb MCP joint

        # For thumb up, thumb tip should be clearly above thumb IP
        thumb_vertical_extension = thumb_ip.y - thumb_tip.y
        if thumb_vertical_extension < 0.05:  # Thumb tip not significantly above IP
            return False

        # Thumb tip should be above the thumb MCP joint
        if thumb_tip.y >= thumb_mcp.y:
            return False

        # Thumb tip should be above all other fingertips (thumb is highest point)
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        for tip_idx in finger_tips:
            if thumb_tip.y >= landmarks[tip_idx].y:  # Thumb not above this fingertip
                return False

        # Other fingers should be closed (fist-like but with thumb up)
        finger_pips = [6, 10, 14, 18]
        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y < landmarks[pip].y:  # Tip is above PIP (finger extended)
                return False

        return True
    
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
                current_time = time.time()
                
                # Right hand thumb up - Left click
                if self.is_thumb_up(landmarks):
                    if current_time - self.last_click_time > self.click_cooldown:
                        pyautogui.click()
                        self.last_click_time = current_time
                
                # Right hand open palm - Scroll down (speed increases as fingers bend)
                elif self.is_open_palm(landmarks):
                    if current_time - self.last_scroll_time > self.scroll_cooldown:
                        # Calculate finger curl amount (how bent the fingers are)
                        curl = self._get_finger_curl(landmarks)
                        # Speed multiplier: 1.0 (straight) to 3.0 (more bent)
                        speed_multiplier = 1.0 + curl * 2.0
                        scroll_amount = int(self.scroll_speed * speed_multiplier)
                        pyautogui.scroll(-scroll_amount)  # Scroll down
                        self.last_scroll_time = current_time
                
                # Right hand victory (two fingers) - Double click
                elif self.is_victory(landmarks):
                    if current_time - self.last_click_time > self.click_cooldown:
                        pyautogui.doubleClick()
                        self.last_click_time = current_time
                
                # Right hand pointing - Move mouse cursor (relative movement)
                elif self.is_pointing(landmarks):
                    index_tip = landmarks[8]
                    # Get finger position in normalized coordinates (0-1 range)
                    # Flip x coordinate to match mirrored display
                    finger_x = 1.0 - index_tip.x
                    finger_y = index_tip.y
                    
                    # Initialize previous position if first time
                    if self.last_finger_x is None or self.last_finger_y is None:
                        self.last_finger_x = finger_x
                        self.last_finger_y = finger_y
                        return  # Skip first frame
                    
                    # Calculate movement delta in normalized coordinates
                    dx = finger_x - self.last_finger_x
                    dy = finger_y - self.last_finger_y
                    
                    # Apply smoothing to movement delta
                    self.smoothed_dx = self.smoothed_dx * self.smoothing_factor + dx * (1 - self.smoothing_factor)
                    self.smoothed_dy = self.smoothed_dy * self.smoothing_factor + dy * (1 - self.smoothing_factor)
                    
                    # Check if movement is significant enough
                    movement_magnitude = abs(self.smoothed_dx) + abs(self.smoothed_dy)
                    
                    if movement_magnitude > self.movement_threshold:
                        # Scale the movement delta to screen pixels
                        # Apply sensitivity multiplier
                        mouse_dx = int(self.smoothed_dx * self.screen_width * self.sensitivity)
                        mouse_dy = int(self.smoothed_dy * self.screen_height * self.sensitivity)
                        
                        # Move mouse relative to current position
                        if mouse_dx != 0 or mouse_dy != 0:
                            pyautogui.moveRel(mouse_dx, mouse_dy, duration=0.01)
                    else:
                        # Movement too small - reset smoothed deltas to prevent drift
                        self.smoothed_dx = 0.0
                        self.smoothed_dy = 0.0
                    
                    # Update previous finger position
                    self.last_finger_x = finger_x
                    self.last_finger_y = finger_y
            
            # LEFT HAND GESTURES
            elif is_left_hand:
                current_time = time.time()
                
                # Left hand thumb up - Nothing
                if self.is_thumb_up(landmarks):
                    pass  # No action
                
                # Left hand pointing - Left click
                elif self.is_pointing(landmarks):
                    if current_time - self.last_click_time > self.click_cooldown:
                        pyautogui.click()  # Left click
                        self.last_click_time = current_time
                
                # Left hand victory - Open Task View
                elif self.is_victory(landmarks):
                    if current_time - self.last_click_time > self.click_cooldown:
                        pyautogui.hotkey('win', 'tab')  # Open Task View
                        self.last_click_time = current_time
                
                # Left hand open palm - Scroll up (speed increases as fingers bend)
                elif self.is_open_palm(landmarks):
                    if current_time - self.last_scroll_time > self.scroll_cooldown:
                        curl = self._get_finger_curl(landmarks)
                        speed_multiplier = 1.0 + curl * 2.0
                        scroll_amount = int(self.scroll_speed * speed_multiplier)
                        pyautogui.scroll(scroll_amount)  # Scroll up
                        self.last_scroll_time = current_time
                
                # Left hand pinch - Nothing
                elif self.is_pinch(landmarks):
                    pass  # No action
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
            
            # Check for dual-fist toggle gesture (both hands showing fists AND far apart)
            both_fists_detected = False
            if detection_result.hand_landmarks and len(detection_result.hand_landmarks) == 2:
                current_time = time.time()
                both_fists = all(self.is_fist(hand_landmarks) for hand_landmarks in detection_result.hand_landmarks)

                # Check if hands are far apart (wrists on opposite sides of frame)
                wrist1_x = detection_result.hand_landmarks[0][0].x
                wrist2_x = detection_result.hand_landmarks[1][0].x
                hands_far_apart = abs(wrist1_x - wrist2_x) > 0.4  # At least 40% of frame width apart

                if both_fists and hands_far_apart:
                    both_fists_detected = True
                    if current_time - self.last_toggle_time > self.toggle_cooldown:
                        self.toggle_control()
                        self.last_toggle_time = current_time

            # Display toggle indicator if both fists detected
            if both_fists_detected:
                toggle_text = "TOGGLE: " + ("Control ON" if self.is_control_active else "Control OFF")
                cv2.putText(frame, toggle_text, (frame.shape[1] // 2 - 100, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

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
                        
                        # Get gesture name
                        gesture_name = self.get_gesture_name(hand_landmarks)
                        
                        # Determine action based on gesture and hand
                        action_text = ""
                        if is_right_hand:
                            if self.is_thumb_up(hand_landmarks):
                                action_text = " - Left Click"
                            elif self.is_open_palm(hand_landmarks):
                                action_text = " - Scroll Down"
                            elif self.is_victory(hand_landmarks):
                                action_text = " - Double Click"
                            elif self.is_pointing(hand_landmarks):
                                action_text = " - Mouse Move"
                        elif is_left_hand:
                            if self.is_pointing(hand_landmarks):
                                action_text = " - Left Click"
                            elif self.is_victory(hand_landmarks):
                                action_text = " - Open Task View"
                            elif self.is_open_palm(hand_landmarks):
                                action_text = " - Scroll Up"
                        
                        gesture_text = f"{hand_label} Hand: {gesture_name}{action_text}"
                        
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
        if hasattr(self, 'cursor_indicator'):
            self.cursor_indicator.destroy()
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    app = HandGestureMouseControl(root)
    root.mainloop()

if __name__ == "__main__":
    main()
