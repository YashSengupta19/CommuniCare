
# CommuniCare

CommuniCare is an innovative healthcare application designed specifically for individuals with paralysis. The application facilitates communication and interaction with the digital world by tracking subtle physical movements, such as **finger lifting, hand tapping, eye blinking, and eye movements**. Through these capabilities, CommuniCare aims to enhance the quality of life for its users by providing a means to communicate effectively and navigate various digital interfaces.

It heavily relies on `OpenCV` and `mediapipe` libraries to track the hands and face movements in real time.


https://github.com/user-attachments/assets/80ca9a13-c6ff-4e85-858b-3e86267e0416



## Files Included


### 1. Configure.py
* Handles the calibration and configuration of eye movement thresholds. It provides methods for setting up thresholds for
    * `EyesOpen`
    * `EyesClosed`
    * `EyesLeft`
    * `EyesRight`
    * `EyesUp`
    * `EyesDown`


### 2. ParalysisMovements.py
* This script designed for tracking eye movements. The script determines various eye actions, such as **blinking, moving left/right/up/down, and eye closure**, using pre-defined threshold values calculated in `Configure.py`. This functionality can be used to simulate **mouse clicks** or **cursor movements** for individuals with paralysis, facilitating digital interaction.
* Features:

  **Eye Blink Detection**: Tracks and counts eye blinks.

https://github.com/user-attachments/assets/d1ecf191-fade-4f79-9586-61b8e9aaafe1


   **Eye Movement Detection**: Identifies eye movements in four directions: left, right, up, and down.
    


https://github.com/user-attachments/assets/6c61c629-98ec-4aa0-824b-52c6cdb1dc80


### 3. HandTrackingModule.py
* This module provides real-time hand tracking using OpenCV and MediaPipe. It detects hand landmarks and configures them to recognize gestures such as lifting specific fingers. This is used for gesture-based controls and other interactive applications.

### 4. EuroFilter.py
* The `EuroFilter` code has been implemented in the hand tracking module. The EuroFilter works like an **averaging filter** and is used to smoothen the fluctuation in the landmarks giving us better threshold values to work with.

### 5. HandTappingModule.py
* The `HandTappingModule` uses a `yolov8` model trained on custom dataset (`best.pt`). The module is used to identify whether the hand is lifted or not. This allows us to count the number of times the person has tapped the table which ultimately corresponds to different functionality.

 https://github.com/user-attachments/assets/ccc828f2-2861-4f9a-b509-835d53619733


### 6. GUI.py
* The GUI.py code provided outlines a Tkinter-based graphical user interface (GUI) for the CommuniCare application, a tool designed to assist individuals with mobility or communication difficulties through voice commands, gesture controls, and other assistive technologies.
* Main Features:
    * **Voice-Controlled Assistant**: Uses text-to-speech to interact with the user.
    * **Tutorial**: Provides instructions on how to use the system.
    * **Gesture-Controlled Keyboard/Mouse**: Uses hand tracking for interaction.
    * **Sending Messages and Making Calls**: Uses WhatsApp for communication.
* Structure:
    * The application is structured using Tkinter frames, with different frames for configuration, tutorials, menus, and app controls.
    * Hand and eye tracking are integrated to control the application through gestures and eye movements.
    * Integration with WhatsApp and other apps is handled via Selenium WebDriver and Chrome options.




