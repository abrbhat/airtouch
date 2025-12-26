# Building the Executable

This guide explains how to package the Hand Gesture Mouse Control application as a standalone Windows executable.

## Prerequisites

1. Install Python 3.7 or higher
2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r build_requirements.txt
   ```

## Building the Executable

### Option 1: Using the Build Script (Recommended)

Simply run:
```bash
python build_exe.py
```

This will create a single executable file in the `dist` folder.

### Option 2: Using PyInstaller Directly

```bash
pyinstaller --name=HandGestureMouseControl --onefile --windowed --add-data="models;models" --hidden-import=mediapipe.tasks.python --hidden-import=mediapipe.tasks.python.vision --hidden-import=mediapipe.tasks.python.core --collect-all=mediapipe --collect-all=opencv-python main.py
```

## Output

After building, you'll find:
- `dist/HandGestureMouseControl.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)
- `HandGestureMouseControl.spec` - PyInstaller spec file (can be used for custom builds)

## Important Notes

1. **Model File**: The `models/hand_landmarker.task` file is automatically included in the executable. Make sure it exists before building.

2. **File Size**: The executable will be large (100-200MB) because it includes:
   - Python interpreter
   - All dependencies (MediaPipe, OpenCV, etc.)
   - MediaPipe model files

3. **First Run**: The first time the executable runs, it may take a few seconds to extract temporary files.

4. **Antivirus**: Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive. You may need to add an exception.

## Distribution

To distribute the app:
1. Share only the `HandGestureMouseControl.exe` file from the `dist` folder
2. Users don't need Python or any dependencies installed
3. They just need to run the `.exe` file

## Troubleshooting

- **"Model not found" error**: Ensure the `models/hand_landmarker.task` file exists before building
- **Large file size**: This is normal for PyInstaller executables with ML libraries
- **Slow startup**: First run extracts files to a temp directory, subsequent runs are faster
- **Missing DLL errors**: Try using `--collect-all` flags for problematic packages

