# Hand Gesture Mouse Control

A desktop application that allows you to control your mouse using hand gestures captured through your webcam.

## Features

- **Dual Hand Control**: Supports both left and right hand gestures simultaneously
- **Right Hand Pointing**: Move the mouse cursor by pointing with your right hand index finger (relative movement)
- **Left Hand Pinch**: Perform left mouse click by pinching thumb and index finger together
- **Left Hand Pointing**: Gesture detection (action can be assigned)
- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand detection
- **Smooth Control**: Built-in smoothing for natural mouse movement
- **Visual Feedback**: Color-coded hand detection (Blue for left, Green for right)

## Requirements

- Python 3.7 or higher
- Webcam
- Windows, macOS, or Linux

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Click "Start Camera" to begin video feed
3. Click "Enable Mouse Control" to activate gesture control
4. Position your hands in front of the camera and use gestures:
   
   **Right Hand Gesture:**
   - **Point with index finger**: Move mouse cursor (relative movement)
   
   **Left Hand Gestures:**
   - **Pinch thumb and index finger**: Left click
   - **Point with index finger**: Detected (no action assigned)

## Controls

- **Start Camera / Stop Camera**: Toggle video feed
- **Enable Mouse Control / Disable Mouse Control**: Toggle gesture control
- **Calibrate**: Set hand position range (optional, for future enhancement)

## Gesture Details

### Right Hand
- **Pointing Gesture**: Extend only your index finger while keeping other fingers closed. Move your hand to control the mouse cursor position. The mouse moves relative to your finger movement (not based on absolute position in the frame). The mouse movement is smoothed for natural control and stops immediately when you stop moving your finger.

### Left Hand
- **Pinch Gesture**: Bring your thumb and index finger together to perform a left mouse click. There's a cooldown period between clicks to prevent accidental multiple clicks.
- **Pointing Gesture**: Extend only your index finger while keeping other fingers closed. This gesture is currently detected but has no assigned action. You can customize this gesture to perform any action you need.

## Tips

- Ensure good lighting for better hand detection
- Keep both hands within the camera frame when using dual-hand gestures
- The application uses smoothing to reduce jittery mouse movements
- The camera feed is mirrored for a more natural experience
- Hand detection is color-coded: Blue for left hand, Green for right hand
- The mouse cursor stops immediately when you stop moving your finger (no sliding effect)

## Troubleshooting

- If the camera doesn't start, make sure no other application is using it
- Adjust lighting if hand detection is inconsistent
- If mouse movement feels too sensitive or not sensitive enough, you can adjust the `smoothing_factor` and `movement_threshold` parameters in the code

## License

This project is open source and available for personal use.

