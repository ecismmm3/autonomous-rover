# autonomous-rover

## Overview

- Autonomous rover prototype capable of autonomous object detection and sample collection
- Devpost Link: https://devpost.com/software/rovert

## Component List
- Raspberry Pi 4 + MicroSD card (x1)
- Wheels (x4)
- DC Motors (x4)
- L298N Dual H Bridge Motor Driver (x2)
- LCD Display w/ I2C interface (x1)
- Servo Motor (x1)
- Ultrasonic Sensor (x1)
- 9V+ Battery
- Jumper Wires
- Custom 3D printed chassis

## Features

### Movement & Sensors
- Sweeps a servo-mounted ultrasonic sensor across 120 degrees and renders a live polar radar map for object detection and terrain mapping
- 4-motor skid-steer via WASD keyboard input, automatically braking when the ultrasonic sensor detects an obstacle within a configurable distance threshold
- Python threading to run sensor polling, servo sweeping, safety monitor, and keyboard input all concurrently with thread-safe shared state managed through a lock

### Robot Arm
- LeRobot SO-101 arm supports both teleoperated and fully autonomous collection modes
    - Calibration: Each motor (assigned a unique ID, but all on the same baudrate), is calibrated across its full range of motion w/ the leader arm
- ROS2 camera pipeline provides live video feedback on custom local network
- Trained via ACT imitation learning algorithm, deployed locally on AMD compute hardware
    - Front & wrist-mounted cameras for two reference frames to prevent erratic movement
    - 50+ demonstration episodes, trained over 300K+ steps

## Files

**```main.py```**: 
- Runs the entire robot in a single unified scrip via Python threading
- Servo sweep + ultrasonic radar display
- Motor control with automatic obstacle detection
- LCD distance readout
- Combined into one file since GPIO pins can only be claimed by one process at a time. Running two scripts at the same time on the same pins causes an OS-level conflict and crashes the program.

**```motor_testing.py```**: 
- Motor setup w/ L298N motor drivers & DC motors
- Defines forward, backward, and stop functions for each motor
- Used for testing individual motor functionality

## Media
