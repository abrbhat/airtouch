# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hand Gesture Mouse Control - a desktop application that controls the mouse using hand gestures captured through a webcam. Uses MediaPipe for hand detection and PyAutoGUI for mouse/keyboard control.

## Commands

**Run the application:**
```bash
python main.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Build executable (Windows):**
```bash
pip install -r build_requirements.txt
python build_exe.py
```

## Architecture

The entire application is in `main.py` as a single `HandGestureMouseControl` class that handles:

- **MediaPipe Hand Detection**: Uses `vision.HandLandmarker` with the tasks API (not the legacy solutions API). Model auto-downloads to `models/hand_landmarker.task` on first run.
- **Gesture Recognition**: Methods like `is_pointing()`, `is_open_palm()`, `is_victory()` detect gestures by analyzing finger landmark positions (tip vs PIP joint y-coordinates).
- **Mouse Control**: Relative mouse movement using smoothing. Right hand pointing moves cursor, left hand pointing clicks.
- **GUI**: Tkinter-based with video feed and settings tabs. Video is flipped horizontally for mirror effect but gesture detection uses unflipped frame.

## Key Implementation Details

- Hand landmarks use normalized coordinates (0-1 range)
- Display frame is flipped but detection runs on original frame
- Left/right hand determined by MediaPipe handedness or wrist x-position fallback
- Hand colors: Blue for left, Green for right
- Cooldown timers prevent gesture spam
- PyAutoGUI failsafe is disabled for smoother control

## Gesture Mapping

| Hand  | Gesture    | Action        |
|-------|------------|---------------|
| Both  | Fist       | Toggle control|
| Right | Pointing   | Move cursor   |
| Right | Open Palm  | Scroll down   |
| Left  | Pointing   | Left click    |
| Left  | Victory    | Win+Tab       |
| Left  | Open Palm  | Scroll up     |
