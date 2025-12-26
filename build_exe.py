"""
Build script to create an executable using PyInstaller
"""
import PyInstaller.__main__
import os
import shutil

# Check if model file exists
if not os.path.exists('models/hand_landmarker.task'):
    print("ERROR: Model file not found!")
    print("Please ensure models/hand_landmarker.task exists before building.")
    print("The model will be downloaded automatically when you run the app for the first time.")
    print("Run 'python main.py' once to download it, then build the executable.")
    exit(1)

# Clean previous builds
print("Cleaning previous builds...")
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('HandGestureMouseControl.spec'):
    os.remove('HandGestureMouseControl.spec')

print("Building executable...")
print("This may take several minutes...")

# PyInstaller arguments
args = [
    'main.py',
    '--name=HandGestureMouseControl',
    '--onefile',  # Create a single executable file
    '--windowed',  # No console window (GUI app)
    '--add-data=models;models',  # Include models directory (Windows uses semicolon)
    '--hidden-import=mediapipe.tasks.python',
    '--hidden-import=mediapipe.tasks.python.vision',
    '--hidden-import=mediapipe.tasks.python.core',
    '--hidden-import=mediapipe.framework.formats',
    '--hidden-import=cv2',
    '--hidden-import=PIL',
    '--hidden-import=pyautogui',
    '--collect-all=mediapipe',  # Collect all mediapipe data files
    '--collect-all=opencv-python',  # Collect all opencv data files
]

PyInstaller.__main__.run(args)

print("\n" + "="*50)
print("Build complete! Executable is in the 'dist' folder.")
print("="*50)
print("\nFile: dist/HandGestureMouseControl.exe")
print("\nNote: The executable is large (~100-200MB) because it includes")
print("all dependencies. This is normal for PyInstaller executables.")

