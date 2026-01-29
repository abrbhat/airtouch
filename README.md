# Hand Gesture Mouse Control

A desktop application that allows you to control your mouse using hand gestures captured through your webcam.

## Features

- **Dual Hand Control**: Supports both left and right hand gestures simultaneously
- **Both Hands Fist (apart)**: Toggle mouse control on/off
- **Right Hand Fist (hold 2s)**: Disable mouse control
- **Right Hand Open Palm**: Enable control + Scroll (palm facing camera = down, back of hand = up)
- **Right Hand Pointing**: Enable control + Move mouse cursor
- **Right Hand Thumb Out**: Left click
- **Right Hand Victory**: Double click
- **Left Hand Pointing**: Left mouse click (requires control active)
- **Left Hand Victory**: Open Task View (requires control active)
- **Left Hand Open Palm**: Scroll up (requires control active)
- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand detection
- **Smooth Control**: Built-in smoothing for natural mouse movement
- **Visual Feedback**: Color-coded hand detection (Blue for left, Green for right) with gesture names and palm orientation
- **Corner Indicator**: Shows ON/OFF status in screen corner when camera is active
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

   **Both Hands:**
   - **Fists (held apart)**: Toggle mouse control on/off

   **Right Hand Gestures (can enable/disable control):**
   - **Fist (hold 2 seconds)**: Disable mouse control
   - **Open palm**: Enable control if off, then scroll (front-facing = down, back-facing = up)
   - **Point with index finger**: Enable control if off, then move mouse cursor
   - **Thumb out** (thumb extended, other fingers closed): Left click (requires control on)
   - **Victory sign** (index and middle fingers extended): Double click (requires control on)

   **Left Hand Gestures (require control to be active):**
   - **Point with index finger**: Left click
   - **Victory sign** (index and middle fingers extended): Open Task View
   - **Open palm** (all fingers extended): Scroll up (curl fingers for faster scroll)

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

### Both Hands
- **Fist Toggle**: Make fists with both hands and hold them apart (at least 40% of frame width). This toggles mouse control on/off. A corner indicator shows the current state.

### Right Hand
Right hand gestures can enable or disable mouse control, allowing single-hand operation.

- **Fist Gesture**: Make a fist and hold for 5 seconds to disable mouse control. The display shows a countdown while holding. This only works when control is currently active.
- **Open Palm Gesture**: Extend all fingers. If control is off, this enables it. If control is on, this scrolls the page. **Palm orientation matters**: palm facing camera scrolls down, back of hand facing camera scrolls up. Curl your fingers slightly to increase scroll speed (up to 3x). The display shows "(FRONT)" or "(BACK)" to indicate detected orientation.
- **Pointing Gesture**: Extend only your index finger while keeping other fingers closed. If control is off, this enables it. If control is on, move your hand to control the mouse cursor. The mouse moves relative to your finger movement (not absolute position). Movement is smoothed for natural control and stops immediately when you stop moving.
- **Thumb Out Gesture**: Extend your thumb outward while keeping other fingers closed. Performs a left mouse click. Requires control to be active.
- **Victory Gesture**: Extend your index and middle fingers (peace sign). Performs a double click. Requires control to be active.

### Left Hand
Left hand gestures only work when mouse control is active.

- **Pointing Gesture**: Extend only your index finger while keeping other fingers closed. Performs a left mouse click. There's a cooldown period between clicks.
- **Victory Gesture**: Extend your index and middle fingers (peace sign). Opens Windows Task View (Win+Tab). There's a cooldown period to prevent multiple triggers.
- **Open Palm Gesture**: Extend all fingers. Scrolls the page up. Curl your fingers slightly to increase scroll speed (up to 3x).

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

