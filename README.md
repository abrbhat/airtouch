# Hand Gesture Mouse Control

A desktop application that allows you to control your mouse using hand gestures captured through your webcam.

## Features

- **Dual Hand Control**: Supports both left and right hand gestures simultaneously
- **Hard/Soft Disable System**: Two-tier disable mechanism for better control
  - **Hard Disable** (red LOCK): Both hands fist - can only be unlocked by both fists
  - **Soft Disable** (orange OFF): Right fist 2s hold - can be unlocked by pointing/palm or both fists
- **Both Hands Fist (apart)**: Lock instantly / Unlock (hold 2s)
- **Right Hand Fist (hold 1s)**: Soft disable control
- **Right Hand Open Palm**: Enable from soft-disable + Scroll (palm = down, back = up)
- **Right Hand Pointing**: Enable from soft-disable + Move mouse cursor
- **Right Hand Thumb Out**: Left click
- **Right Hand Victory**: Open Task View (Win+Tab)
- **Left Hand Pointing**: Left mouse click (requires control active)
- **Left Hand Victory**: Open Task View (requires control active)
- **Left Hand Open Palm**: Scroll up (requires control active)
- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand detection
- **Smooth Control**: Built-in smoothing for natural mouse movement
- **Visual Feedback**: Color-coded hand detection (Blue for left, Green for right) with gesture names and palm orientation
- **Corner Indicator**: Shows 3 states - Green ON, Orange OFF (soft), Red LOCK (hard)
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
   - **Fists (held apart)**: Lock instantly when ON / Hold 2s to unlock

   **Right Hand Gestures:**
   - **Fist (hold 1 second)**: Soft disable (orange indicator) - only when ON
   - **Open palm**: Enable from soft-disable, then scroll (front = down, back = up)
   - **Point with index finger**: Enable from soft-disable, then move mouse cursor
   - **Thumb out** (thumb extended, other fingers closed): Left click (requires ON)
   - **Victory sign** (index and middle fingers extended): Open Task View (requires ON)

   Note: Pointing/palm cannot unlock hard-disabled (red LOCK) state - use both fists

   **Left Hand Gestures (require control to be ON):**
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

### Control States
The system has three states indicated by the corner indicator:
- **Green ON**: Control is active, all gestures work
- **Orange OFF (Soft Disabled)**: Can be re-enabled by right hand pointing or open palm
- **Red LOCK (Hard Disabled)**: Can only be unlocked by both hands fist gesture

### Both Hands
- **Fist Toggle**: Make fists with both hands and hold them apart (at least 40% of frame width). When ON, this instantly locks (red). When disabled, hold for 2 seconds to unlock. Display shows countdown.

### Right Hand
Right hand gestures can enable or soft-disable mouse control, allowing single-hand operation.

- **Fist Gesture**: Make a fist and hold for 1 second to soft-disable mouse control (orange OFF). The display shows a countdown while holding. This only works when control is ON.
- **Open Palm Gesture**: Extend all fingers. If soft-disabled (orange), this enables control. If hard-disabled (red LOCK), this does nothing. If ON, this scrolls the page. **Palm orientation matters**: palm facing camera scrolls down, back of hand facing camera scrolls up.
- **Pointing Gesture**: Extend only your index finger. If soft-disabled (orange), this enables control. If hard-disabled (red LOCK), this does nothing. If ON, move your hand to control the mouse cursor.
- **Thumb Out Gesture**: Extend your thumb outward while keeping other fingers closed. Performs a left mouse click. Requires control to be ON.
- **Victory Gesture**: Extend your index and middle fingers (peace sign). Opens Windows Task View (Win+Tab). Requires control to be ON.

### Left Hand
Left hand gestures only work when mouse control is ON (green indicator).

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

