# Face Tracking Robot Arm

A robotic arm that tracks a human face in real time using computer vision.

Built using Python, OpenCV, Arduino, and a Hiwonder robotic arm.

## Features

- Real-time face detection
- Camera-based tracking
- Pan and tilt movement
- Adjustable tracking sensitivity
- Face-centered stopping zone

## Hardware

- Hiwonder robotic arm
- Arduino
- Mac mini
- Camera
- Jumper wires

## How It Works

1. The camera captures live video.
2. OpenCV detects a face.
3. Python calculates the face's position relative to the center of the camera.
4. Movement commands are sent to the Arduino over serial.
5. The Arduino moves the arm to follow the face.

## Software

- Python
- OpenCV
- PySerial
- Arduino

## Installation

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Upload the Arduino sketch from the `arduino` directory.

Run the tracker:

```bash
python python/face_tracker.py
```

Press `Q` to exit.

## Project Status

This is an ongoing robotics project. Tracking sensitivity, movement speed, and face detection are still being improved.

Created as a personal robotics and computer vision project.
