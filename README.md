# Hand Gesture Mouse Control

A desktop application that allows you to control your mouse using hand gestures captured through your webcam.

## Features

- **Dual Hand Control**: Supports both left and right hand gestures simultaneously
- **Right Hand Open Palm**: Scroll down
- **Right Hand Victory**: Open Task View (Windows)
- **Right Hand Pointing**: Move the mouse cursor by pointing with your right hand index finger (relative movement)
- **Left Hand Pointing**: Left mouse click
- **Left Hand Victory**: Right mouse click
- **Left Hand Open Palm**: Scroll up
- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand detection
- **Smooth Control**: Built-in smoothing for natural mouse movement
- **Visual Feedback**: Color-coded hand detection (Blue for left, Green for right) with gesture names
- **Settings Tab**: Adjustable parameters in real-time (scroll speed, sensitivity, smoothing, etc.)

## Requirements

- Python 3.7 or higher
- Webcam
- Windows, macOS, or Linux

## Installation

### Option 1: Run from Source

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Use Pre-built Executable

If available, you can use a pre-built Windows executable (`HandGestureMouseControl.exe`) that doesn't require Python installation. Simply download and run the `.exe` file.

### Building Your Own Executable

To create your own executable, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed instructions.

## Usage

1. Run the application:
```bash
python main.py
```

2. Click "Start Camera" to begin video feed
3. Click "Enable Mouse Control" to activate gesture control
4. Position your hands in front of the camera and use gestures:
   
   **Right Hand Gestures:**
   - **Open palm** (all fingers extended): Scroll down
   - **Victory sign** (index and middle fingers extended): Open Task View
   - **Point with index finger**: Move mouse cursor (relative movement)
   
   **Left Hand Gestures:**
   - **Point with index finger**: Left click
   - **Victory sign** (index and middle fingers extended): Right click
   - **Open palm** (all fingers extended): Scroll up

5. **Adjust Settings**: Click on the "Settings" tab to adjust parameters in real-time:
   - Scroll Speed: Control how much scrolling occurs per gesture
   - Mouse Sensitivity: Adjust how much the mouse moves relative to finger movement
   - Smoothing: Control mouse movement smoothness
   - Movement Threshold: Minimum movement required to trigger mouse movement
   - Click Cooldown: Time between clicks
   - Scroll Cooldown: Time between scroll actions

## Controls

- **Start Camera / Stop Camera**: Toggle video feed
- **Enable Mouse Control / Disable Mouse Control**: Toggle gesture control
- **Settings Tab**: Adjust all parameters in real-time without restarting the application

## Gesture Details

### Right Hand
- **Open Palm Gesture**: Extend all fingers (thumb, index, middle, ring, and pinky). This gesture scrolls the page down. The scroll speed can be adjusted in the Settings tab.
- **Victory Gesture**: Extend your index and middle fingers while keeping other fingers closed (peace sign). This gesture opens Windows Task View (Win+Tab). There's a cooldown period to prevent multiple triggers.
- **Pointing Gesture**: Extend only your index finger while keeping other fingers closed. Move your hand to control the mouse cursor position. The mouse moves relative to your finger movement (not based on absolute position in the frame). The mouse movement is smoothed for natural control and stops immediately when you stop moving your finger.

### Left Hand
- **Pointing Gesture**: Extend only your index finger while keeping other fingers closed. This gesture performs a left mouse click. There's a cooldown period between clicks to prevent accidental multiple clicks.
- **Victory Gesture**: Extend your index and middle fingers while keeping other fingers closed (peace sign). This gesture performs a right mouse click. There's a cooldown period to prevent multiple clicks.
- **Open Palm Gesture**: Extend all fingers (thumb, index, middle, ring, and pinky). This gesture scrolls the page up. The scroll speed can be adjusted in the Settings tab.

## Tips

- Ensure good lighting for better hand detection
- Keep both hands within the camera frame when using dual-hand gestures
- The application uses smoothing to reduce jittery mouse movements
- The camera feed is mirrored for a more natural experience
- Hand detection is color-coded: Blue for left hand, Green for right hand
- The mouse cursor stops immediately when you stop moving your finger (no sliding effect)
- Use the Settings tab to fine-tune parameters for your preferences:
  - Increase sensitivity if mouse movement feels too slow
  - Increase smoothing if movement is too jittery
  - Adjust scroll speed to match your scrolling needs
  - Modify cooldowns to prevent accidental actions

## Troubleshooting

- If the camera doesn't start, make sure no other application is using it
- Adjust lighting if hand detection is inconsistent
- If mouse movement feels too sensitive or not sensitive enough, use the Settings tab to adjust parameters in real-time
- If scrolling is too fast or slow, adjust the Scroll Speed in the Settings tab
- If gestures are triggering too frequently, increase the cooldown values in Settings

## License

This project is open source and available for personal use.

