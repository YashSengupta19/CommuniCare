import tkinter as tk
import threading
import logging
import time
import os
from PIL import Image, ImageTk
import cv2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pyttsx3
from pynput.mouse import Button, Controller

# Custom modules
import Configure as cf
import HandTrackingModule as htm
import HandTappingModule as httm
import ParalysisMovements as pm
from config import CHROME_DATA_PATH
from Keyboard import KeyBoard
import json

logging.basicConfig(level=logging.INFO)

# Main GUI class
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.transition_id = None
        self.rotation_id = None

        self.title("CommuniCare")
        self.geometry("1440x1080")

        self.welcome_frame = tk.Frame(self)
        self.welcome_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.welcome_frame, text="Welcome to CommuniCare", font=("Helvetica", 30))
        self.label.pack(pady=200)
                
        # Initializing the Objects
        self.eye_configure = cf.Configure()
        self.hand_tracker = htm.HandDetector()
        self.hand_tap_detector = httm.HandTappingModule()
        
        # Initializing various flags indicating which functionality is active in which frame
        self.MOUSE_MOTION = False
        self.KEYBOARD = False
        self.EXPLAIN_TUTORIAL = True
        self.BUTTON_CLICK = True
        self.SEND_PRIMARY_MESSAGE = False
        self.USE_SECONDARY_FUNCTIONS = False
        
        self.mouse = Controller()
        self.driver = None
        self.thread = None
        
        self.video_capture = cv2.VideoCapture(0)
        
        self.after(1000, self.welcome_message)
        
    def welcome_message(self):
        self.text_to_speech("Welcome to CommuniCare. We will begin with the configuration. We will start configuring your eyes first. Please follow the instructions written on the screen.")
        self.after(2000, self.show_configure)
        
    def explain_tutorial(self):
        self.text_to_speech("Communicare assists you in communicating effectively with your caregivers and navigating the digital world.\
                            There are two types of commands: Primary and Secondary. Primary Commands: These require the assistance of a\
                            caregiver. Examples include requesting food, water, or emergency help. These commands are detected through\
                            tapping, with the number of taps indicating which command is executed. A message is then sent to the\
                            caregiver's number. Secondary Commands: These commands assist you in navigating your phone or laptop using\
                            limited movements. Detailed instructions for these commands will be provided when you start using the services.")
        self.EXPLAIN_TUTORIAL = False
            
        self.transition_id = self.after(3000, self.show_option2)
    
    def button_click(self):
        self.text_to_speech("The button when it is blue is active. Blink once when the button is active to select it.")

        
    def text_to_speech(self, text):
        engine = pyttsx3.init()
        
        engine.setProperty('rate', value=150)
        engine.setProperty('volume', value=1)
        
        engine.say(text)
        
        engine.runAndWait()
                
    def show_menu(self):
        
        self.BUTTON_CLICK = True
        self.after(1000, self.text_to_speech, "The button when it is blue is active. Blink once when the button is active to select it.")
        
        self.clear_frames()
        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.menu_frame, text="Do you want a Tutorial?", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_option1 = tk.Button(self.menu_frame, text="Yes", font=("Helvetica", 20), command=self.show_option1)
        self.btn_option1.pack(pady=20)

        self.btn_option2 = tk.Button(self.menu_frame, text="No", font=("Helvetica", 20), command=self.show_option2)
        self.btn_option2.pack(pady=20)

        self.rotate_buttons([self.btn_option1, self.btn_option2])
        
        self.process_frame_for_blinks([self.btn_option1, self.btn_option2])

    def show_option1(self):
        
        self.BUTTON_CLICK = False
        
        self.clear_frames()
        self.option1_frame = tk.Frame(self)
        self.option1_frame.pack(fill="both", expand=True)

        
        img = Image.open("C:\\Users\\jishu\\OneDrive\\Desktop\\PythonCodes\\TutorialIMG.png")
        img_tk = ImageTk.PhotoImage(img)
        label = tk.Label(self.option1_frame, image=img_tk)
        label.image = img_tk  # Keep a reference to prevent garbage collection
        label.pack()

        self.btn_back = tk.Button(self.option1_frame, text="Back to Menu", font=("Helvetica", 15), command=lambda: self.go_back(self.option1_frame, self.show_menu))
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')

        if self.EXPLAIN_TUTORIAL:
            self.after(1000, self.explain_tutorial)

    def show_option2(self):
        
        self.SEND_PRIMARY_MESSAGE = False
        self.BUTTON_CLICK = False
        
        self.clear_frames()
        self.option2_frame = tk.Frame(self)
        self.option2_frame.pack(fill="both", expand=True)
    
        self.label = tk.Label(self.option2_frame, text="Menu", font=("Helvetica", 20))
        self.label.pack(pady=50)
    
        self.btn_option2_1 = tk.Button(self.option2_frame, text="Food", font=("Helvetica", 20), command=self.show_food_menu)
        self.btn_option2_1.pack(pady=20)
    
        self.btn_option2_2 = tk.Button(self.option2_frame, text="Emergency", font=("Helvetica", 20), command=self.show_emergency_menu)
        self.btn_option2_2.pack(pady=20)
    
        self.btn_option2_3 = tk.Button(self.option2_frame, text="Water", font=("Helvetica", 20), command=self.show_water_menu)
        self.btn_option2_3.pack(pady=20)
    
        self.btn_option2_4 = tk.Button(self.option2_frame, text="Apps", font=("Helvetica", 20), command=self.show_apps_menu)
        self.btn_option2_4.pack(pady=20)
    
        self.btn_back = tk.Button(self.option2_frame, text="Back to Menu", font=("Helvetica", 15), command=self.show_menu)
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')
    
        # Start frame processing for hand tap detection
        self.after(1000, self.process_frame_for_taps)

    # Processes each frame captured for blinks
    def process_frame_for_taps(self):
        success, image = self.video_capture.read()
        if not success:
            print("Failed to read frame from camera. Exiting...")
            self.update_configure_label("Configuration Failed")
            return
    
        image = cv2.resize(image, (1000, 1000))
        image = cv2.flip(image, 1)
    
        if self.hand_tap_detector.make_prediction(image):
            tapCount = self.hand_tap_detector.detectTap(self.hand_tap_detector.make_prediction(image))
    
        if tapCount == 1:
            self.show_food_menu()
            return
        elif tapCount == 2:
            self.show_emergency_menu()
            return
        elif tapCount == 3:
            self.show_water_menu()
            return
        elif tapCount == 4:
            self.show_apps_menu()
            return
    
        self.after(10, self.process_frame_for_taps)
    
    # Processes each Frame captured for taps
    def process_frame_for_blinks(self, buttons):
        
        success, image = self.video_capture.read()
        if not success:
            print("Failed to read frame from camera. Exiting...")
            self.update_configure_label("Configuration Failed")
            return
    
        image = cv2.resize(image, (1000, 1000))
        image = cv2.flip(image, 1)
        
        results, landmarks = self.eye_movements.get_landmarks(image)
        
        if landmarks:
            
            if self.eye_movements.did_Blink(landmarkA=landmarks[160], landmarkB=landmarks[144]):
                
                for i, button in enumerate(buttons):
                    if button.cget("state") == "normal":
                        button.invoke()
                        
        
        
        if self.BUTTON_CLICK:
            self.after(1, self.process_frame_for_blinks, buttons)
            
    def speak_primary_message(self, text):
        if self.SEND_PRIMARY_MESSAGE:
            self.text_to_speech(text)
            self.after(2000, self.speak_primary_message, text)
        
    
    # Used to send WhatsApp messages in headless mode
    def send_whatsapp_headlessmessage(self, phone_number, message):
        
        self.speak_primary_message(message)
        
        def run_whatsapp():
            try:
                os.system("taskkill /im chrome.exe /f")
                options = webdriver.ChromeOptions()
                options.add_argument(CHROME_DATA_PATH)
                options.add_argument("--headless=new")
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')

                s = Service(executable_path="chromedriver-win64\chromedriver.exe")
                driver = webdriver.Chrome(service=s, options=options)
                driver.get("https://web.whatsapp.com/")
                time.sleep(15)

                search_icon = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[3]/div/div[1]/div/div[2]/button")
                search_icon.click()
                time.sleep(2)

                search_new_chat = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[3]/div/div[1]/div/div[2]/div[2]/div/div[1]/p")
                search_new_chat.send_keys(phone_number)
                time.sleep(2)
               
                first_name = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div/div[1]")
                first_name.click()
                time.sleep(2)

                msg_send_key = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p")
                msg_send_key.send_keys(message)
                time.sleep(2)

                send_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button")
                send_button.click()
                time.sleep(2)

                logging.info("Message sent successfully!")
            except Exception as e:
                logging.error(f"Error sending WhatsApp message: {e}")
        
        thread = threading.Thread(target=run_whatsapp)
        thread.start()
        # thread.join()
            
        # if self.SEND_PRIMARY_MESSAGE:
        #     self.after(1000, self.send_whatsapp_headlessmessage, phone_number, message)


    def show_food_menu(self):
        self.SEND_PRIMARY_MESSAGE = True
        self.clear_frames()
        self.food_frame = tk.Frame(self)
        self.food_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.food_frame, text="Food Menu", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_back = tk.Button(self.food_frame, text="Back to Menu", font=("Helvetica", 15), command=self.show_option2)
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')
        
        self.after(3000, self.send_whatsapp_headlessmessage, "916291798504", "I want something to eat\n") # Sends a message to caretaker through WhatsApp in headless mode

    def show_emergency_menu(self):
        self.SEND_PRIMARY_MESSAGE = True
        self.clear_frames()
        self.emergency_frame = tk.Frame(self)
        self.emergency_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.emergency_frame, text="Emergency Menu", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_back = tk.Button(self.emergency_frame, text="Back to Menu", font=("Helvetica", 15), command=self.show_option2)
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')
        
        self.after(3000, self.send_whatsapp_headlessmessage, "916291798504", "I need help\n")

    def show_water_menu(self):
        self.SEND_PRIMARY_MESSAGE = True
        self.clear_frames()
        self.water_frame = tk.Frame(self)
        self.water_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.water_frame, text="Water Menu", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_back = tk.Button(self.water_frame, text="Back to Menu", font=("Helvetica", 15), command=self.show_option2)
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')
        
        self.after(3000, self.send_whatsapp_headlessmessage, "916291798504", "I need some water\n")

    def show_apps_menu(self):
        
        self.USE_SECONDARY_FUNCTIONS = False
        self.BUTTON_CLICK = True
        
        self.clear_frames()
        self.apps_frame = tk.Frame(self)
        self.apps_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.apps_frame, text="Apps Menu", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_option2_4_1 = tk.Button(self.apps_frame, text="Youtube", font=("Helvetica", 20), command=self.show_youtube)
        self.btn_option2_4_1.pack(pady=20)

        self.btn_option2_4_2 = tk.Button(self.apps_frame, text="Whatsapp", font=("Helvetica", 20), command=self.show_whatsapp)
        self.btn_option2_4_2.pack(pady=20)

        self.btn_option2_4_3 = tk.Button(self.apps_frame, text="Netflix", font=("Helvetica", 20), command=self.show_netflix)
        self.btn_option2_4_3.pack(pady=20)

        self.btn_back = tk.Button(self.apps_frame, text="Back to Menu", font=("Helvetica", 15), command=self.show_option2)
        self.btn_back.pack(pady=20)
        
        self.after(10, self.text_to_speech, "You can control the cursor using your eyes. Look where you want to move\
                   the cursor and blink once to select it. Keep in mind that you must lift your index finger in order to\
                       move the cursor.")


        self.rotate_buttons([self.btn_option2_4_1, self.btn_option2_4_2, self.btn_option2_4_3, self.btn_back])
        
        self.process_frame_for_blinks([self.btn_option2_4_1, self.btn_option2_4_2, self.btn_option2_4_3, self.btn_back])

    # Youtube GUI
    def show_youtube(self):
        
        self.text_to_speech("Opening Youtube")
        self.USE_SECONDARY_FUNCTIONS = True
        self.BUTTON_CLICK = False
        
        self.clear_frames()
        self.youtube_frame = tk.Frame(self)
        self.youtube_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.youtube_frame, text="Youtube", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_back = tk.Button(self.youtube_frame, text="Back to Apps Menu", font=("Helvetica", 15), command=self.show_apps_menu)
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')
        
        def open_youtube():
            os.system("taskkill /im chrome.exe /f")
            options = Options()
            options.add_argument(CHROME_DATA_PATH)
            options.add_experimental_option("detach", True)

            s = Service(executable_path="chromedriver-win64/chromedriver.exe")
            self.driver = webdriver.Chrome(service=s, options=options)
            self.driver.get("https://www.youtube.com/")
            time.sleep(15)
            
        
        thread = threading.Thread(target=open_youtube)
        thread.start()
        
        self.after(20000, self.use_youtube)
    
    # This function allows us to use youtube using eye and finger motion
    def use_youtube(self):
        
        success, image = self.video_capture.read()
        if not success:
            print("Failed to read frame from camera. Exiting...")
            self.update_configure_label("Cannot Open WhatsApp")
            return
    
        image = cv2.resize(image, (1000, 1000))
        image = cv2.flip(image, 1)
        
        finger_list = self.hand_tracker.get_finger_lmllist(image)
        if len(finger_list) != 0:
            if self.hand_tracker.isIndex(finger_list[1]):
                self.MOUSE_MOTION = True
                print("Index")
            else:
                self.MOUSE_MOTION = False
        
        results, landmarks = self.eye_movements.get_landmarks(image)
        
        if self.MOUSE_MOTION:
            if landmarks:
                if self.eye_movements.eye_left(landmarks[469]):
                    self.mouse.move(-5, 0)
                if self.eye_movements.eye_right(landmarks[469]):
                    self.mouse.move(5, 0)
                if self.eye_movements.eye_up(landmarks[469]):
                    self.mouse.move(0, -5)
                if self.eye_movements.eye_down(landmarks[469]):
                    self.mouse.move(0, 5)
        
        if self.eye_movements.did_Blink(landmarkA=landmarks[160], landmarkB=landmarks[144]):
            self.mouse.click(Button.left, 1)
    
        
        if self.USE_SECONDARY_FUNCTIONS:
            self.after(1, self.use_youtube)

    # Display WhatsApp
    def show_whatsapp(self):
        
        self.text_to_speech("Opening Whatsapp")
        self.USE_SECONDARY_FUNCTIONS = True
        self.BUTTON_CLICK = False
        
        self.clear_frames()
        self.whatsapp_frame = tk.Frame(self)
        self.whatsapp_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.whatsapp_frame, text="Whatsapp", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_back = tk.Button(self.whatsapp_frame, text="Back to Apps Menu", font=("Helvetica", 15), command=self.show_apps_menu)
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')
        
        def open_whatsapp():
            os.system("taskkill /im chrome.exe /f")
            options = Options()
            options.add_argument(CHROME_DATA_PATH)
            options.add_experimental_option("detach", True)

            s = Service(executable_path="chromedriver-win64/chromedriver.exe")
            self.driver = webdriver.Chrome(service=s, options=options)
            self.driver.get("https://web.whatsapp.com/")
            time.sleep(15)
            
            script = """
            document.addEventListener('click', function(event) {
                var clickedElement = event.target;
                var elementInfo = {
                    tag: clickedElement.tagName,
                    id: clickedElement.id,
                    class: clickedElement.className,
                    text: clickedElement.innerText,
                    html: clickedElement.outerHTML
                    };
                window.localStorage.setItem('clickedElementInfo', JSON.stringify(elementInfo));
                }, true);
            """
            
            self.driver.execute_script(script)
        
        thread = threading.Thread(target=open_whatsapp)
        thread.start()
        
        self.after(20000, self.use_whatsapp, self.driver)
        
    # Opens the WhatsApp page
    
    def use_whatsapp(self, driver):
        
        success, image = self.video_capture.read()
        if not success:
            print("Failed to read frame from camera. Exiting...")
            self.update_configure_label("Cannot Open WhatsApp")
            return
    
        image = cv2.resize(image, (1000, 1000))
        image = cv2.flip(image, 1)
        
        finger_list = self.hand_tracker.get_finger_lmllist(image)
        if len(finger_list) != 0:
            if self.hand_tracker.isIndex(finger_list[1]):
                self.MOUSE_MOTION = True
                print("Index")
            else:
                self.MOUSE_MOTION = False
        
        results, landmarks = self.eye_movements.get_landmarks(image)
        
        if self.MOUSE_MOTION:
            if landmarks:
                if self.eye_movements.eye_left(landmarks[469]):
                    self.mouse.move(-5, 0)
                if self.eye_movements.eye_right(landmarks[469]):
                    self.mouse.move(5, 0)
                if self.eye_movements.eye_up(landmarks[469]):
                    self.mouse.move(0, -5)
                if self.eye_movements.eye_down(landmarks[469]):
                    self.mouse.move(0, 5)
        
        if self.eye_movements.did_Blink(landmarkA=landmarks[160], landmarkB=landmarks[144]):
            self.mouse.click(Button.left, 1)
        
        # clicked_element_info = driver.execute_script("return window.localStorage.getItem('clickedElementInfo');")

        # if clicked_element_info:
        #     element_info = json.loads(clicked_element_info)
            
        #     if "selectable-text copyable-text x15bjb6t x1n2onr6" in element_info["class"]:
        #         if not self.KEYBOARD:
        #             print("Clicked on the specified element!")
        #             keyboard = KeyBoard()
        #             typed_text = keyboard.get_typed_text()  
        #             print("Typed text:", typed_text)
        #             if typed_text != "":
                        
        #                 if "search input class name" in element_info["class"]:
        #                     msgSendKey = driver.find_element(By.CLASS_NAME, "search input class name")
        #                 else:
        #                     msgSendKey = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p")
     
        #                     msgSendKey.send_keys(typed_text)
        #                     msgSendKey.send_keys(Keys.RETURN)
        #                     print("Typed and sent the message")
        #                     time.sleep(5)
        
        #             self.KEYBOARD = True
            
        #     else:
        #         self.KEYBOARD = False
     
        # # Clear the localStorage entry after processing
        # driver.execute_script("window.localStorage.removeItem('clickedElementInfo');")
     
        # # Short sleep to prevent high CPU usage
        # time.sleep(0.1)
        
        if self.USE_SECONDARY_FUNCTIONS:
            self.after(1, self.use_whatsapp, self.driver)

    # Opens the netflix page
    def show_netflix(self):
        
        self.USE_SECONDARY_FUNCTIONS = True
        self.BUTTON_CLICK = False
        
        self.clear_frames()
        self.netflix_frame = tk.Frame(self)
        self.netflix_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.netflix_frame, text="Netflix", font=("Helvetica", 20))
        self.label.pack(pady=50)

        self.btn_back = tk.Button(self.netflix_frame, text="Back to Apps Menu", font=("Helvetica", 15), command=self.show_apps_menu)
        self.btn_back.pack(pady=20)
        self.btn_back.config(bg='lightblue')

    def show_configure(self):
        self.clear_frames()

        self.configure_frame = tk.Frame(self)
        self.configure_frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.configure_frame, text="We will begin configuring", font=("Helvetica", 20))
        self.label.pack(pady=10)
        
        self.video_label = tk.Label(self.configure_frame)
        self.video_label.pack(padx=100, pady=10)
        
        self.eye_process_frame()
        
    # This function runs in background and processes the eye landmarks

    def eye_process_frame(self):
        
        success, image = self.video_capture.read()
        if not success:
            print("Failed to read frame from camera. Exiting...")
            self.update_configure_label("Configuration Failed")
            return
        
        image = cv2.resize(image, (1000, 1000))
        image = cv2.flip(image, 1)

        self.results, self.landmarks = self.eye_configure.get_landmarks(image)

        if self.landmarks:
            if self.eye_configure.eye_open_config:
                cv2.putText(image, "Please Keep Your Eyes Open", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                done = self.eye_configure.configure_eye_open(self.landmarks[160], self.landmarks[144])
                if done:
                    self.after(2000, self.eye_process_frame)
                    return

            elif self.eye_configure.eye_closed_config: 
                cv2.putText(image, "Please Close Your Eyes", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                done = self.eye_configure.configure_eye_closed(self.landmarks[160], self.landmarks[144])
                if done:
                    self.after(2000, self.eye_process_frame)
                    return

            elif self.eye_configure.left_config:
                cv2.putText(image, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(image, (20, int(self.eye_configure.imageheight / 2)), 20, (0, 0, 255), -1)
                done = self.eye_configure.configure_eye_left(self.landmarks[468])
                if done:
                    self.after(20, self.eye_process_frame)
                    return

            elif self.eye_configure.right_config:
                cv2.putText(image, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(image, (int(self.eye_configure.imagewidth - 20), int(self.eye_configure.imageheight / 2)), 20, (0, 0, 255), -1)
                done = self.eye_configure.configure_eye_right(self.landmarks[468])
                if done:
                    self.after(20, self.eye_process_frame)
                    return

            elif self.eye_configure.up_config:
                cv2.putText(image, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(image, (int(self.eye_configure.imagewidth / 2), 20), 20, (0, 0, 255), -1)
                done = self.eye_configure.configure_eye_up(self.landmarks[468])
                if done:
                    self.after(20, self.eye_process_frame)
                    return

            elif self.eye_configure.down_config:
                cv2.putText(image, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(image, (int(self.eye_configure.imagewidth / 2), int(self.eye_configure.imageheight - 20)), 20, (0, 0, 255), -1)
                done = self.eye_configure.configure_eye_down(self.landmarks[468])
                if done:
                    self.after(20, self.eye_process_frame)
                    return

            else:
                self.eye_movements = pm.ParalysisMovements(eye_closed= self.eye_configure.eye_closed, 
                                                           eye_open= self.eye_configure.eye_open,
                                                           eye_left_threshold= self.eye_configure.left,
                                                           eye_right_threshold= self.eye_configure.right,
                                                           eye_up_threshold= self.eye_configure.up,
                                                           eye_down_threshold= self.eye_configure.down)
                print(self.eye_configure.eye_closed, self.eye_configure.eye_open)
                self.label.config(text="Configuring Hands")
                self.after(1000, self.text_to_speech("Now we will be configuring your hands. Please keep the hands on the table so that they are visible."))
                self.after(2000, self.hand_process_frame)
                return

        # Convert the image to RGB and then to PIL format for Tkinter
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        # Update the label with the new image
        self.video_label.config(image=image)
        self.video_label.image = image

        # Continue processing the next frame
        self.after(10, self.eye_process_frame)
    
    # This function runs in background and processes the hand landmarks
    def hand_process_frame(self):
        success, image = self.video_capture.read()
        if not success:
            print("Failed to read frame from camera. Exiting...")
            self.update_configure_label("Configuration Failed")
            return
        
        image = cv2.resize(image, (1000, 1000))
        image = cv2.flip(image, 1)
        
        self.lml_list = self.hand_tracker.get_finger_lmllist(image)
        
        if len(self.lml_list) != 0:
            image = self.hand_tracker.drawHands(image, self.lml_list)
            if not self.hand_tracker.leftHand_config:
                image = self.hand_tracker.left_hand_configure(self.lml_list, image)
            else:
                self.update_configure_label("Configuration Done")
                
                self.after(2000, self.show_menu)
                return
            
        # Convert the image to RGB and then to PIL format for Tkinter
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
    
        # Update the label with the new image
        self.video_label.config(image=image)
        self.video_label.image = image
    
        # Continue processing the next frame
        self.after(10, self.hand_process_frame)
        

    def update_configure_label(self, new_text):
        for widget in self.configure_frame.winfo_children():
            widget.destroy()
        self.label = tk.Label(self.configure_frame, text=new_text, font=("Helvetica", 30))
        self.label.pack(pady=200)

    # Returns to the previous frame
    def go_back(self, current_frame, back_function):
        if self.transition_id is not None:
            self.after_cancel(self.transition_id)
            self.transition_id = None
        if self.rotation_id is not None:
            self.after_cancel(self.rotation_id)
            self.rotation_id = None
        current_frame.destroy()
        back_function()

    def clear_frames(self):
        for widget in self.winfo_children():
            widget.destroy()

    # This function makes the each button activate for sometime before deactivating it
    # The idea is if we blink in the duration when the button is activated then it will be selected
    
    def rotate_buttons(self, buttons):
        if hasattr(self, 'current_button'):
            current_index = self.current_button
        else:
            current_index = -1

        next_index = (current_index + 1) % len(buttons)
        self.current_button = next_index

        for i, btn in enumerate(buttons):
            if i == next_index:
                btn.config(bg="lightblue", state="normal")
            else:
                btn.config(bg='white', state="disabled")

        self.rotation_id = self.after(2000, lambda: self.rotate_buttons(buttons))

if __name__ == "__main__":
    app = GUI()
    app.mainloop()