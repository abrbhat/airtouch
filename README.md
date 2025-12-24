# Hand Gesture Mouse Control

A desktop application that allows you to control your mouse using hand gestures captured through your webcam.

## Features

- **Mouse Movement**: Point with your index finger to move the mouse cursor
- **Left Click**: Pinch your thumb and index finger together
- **Right Click**: Extend all five fingers (open hand)
- **Middle Click**: Make a fist
- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand detection
- **Smooth Control**: Built-in smoothing for natural mouse movement

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
4. Position your hand in front of the camera and use gestures:
   - **Point with index finger**: Move mouse cursor
   - **Pinch thumb and index**: Left click
   - **Open hand (5 fingers)**: Right click
   - **Fist**: Middle click

## Controls

- **Start Camera / Stop Camera**: Toggle video feed
- **Enable Mouse Control / Disable Mouse Control**: Toggle gesture control
- **Calibrate**: Set hand position range (optional, for future enhancement)

## Tips

- Ensure good lighting for better hand detection
- Keep your hand within the camera frame
- The application uses smoothing to reduce jittery mouse movements
- There's a cooldown between clicks to prevent accidental multiple clicks

## Troubleshooting

- If the camera doesn't start, make sure no other application is using it
- Adjust lighting if hand detection is inconsistent
- You may need to adjust the `click_threshold` in the code if clicks aren't registering properly

## License

This project is open source and available for personal use.

