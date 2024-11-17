import cv2
import mediapipe as mp
import numpy as np
import EuroFIlter as ef
import time

class HandDetector():
    def __init__(self, mode = False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5): # The parameters are the basic parameters that are required for the hands
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)        
        self.mpDraw = mp.solutions.drawing_utils 
        
        self.handLifted = float('-inf')
        self.leftIndex = float('-inf')
        self.leftThumb = float('-inf')
        self.leftMiddle = float('-inf')
        self.leftRing = float('-inf')
        self.leftPinky = float('-inf')
        
        self.leftThumb_config = True
        self.leftIndex_config = False
        self.leftMiddle_config = False
        self.leftRing_config = False
        self.leftPinky_config = False
        self.leftHand_config = False
        self.isHands_stable = False
        
        self.iterations = 0
        
        self.stability_buffer_size = 30  # Number of frames to check for stability
        self.stability_threshold = 100  # Threshold for the variance to consider the hand stable
        self.stability_buffer = {i: [] for i in range(5)}  # Buffer to store positions for each finger
        
        self.eurofilter_x = ef.OneEuroFilter()
        self.eurofilter_y = ef.OneEuroFilter()

    # Detection Part
    def findHands(self, img, draw = True): 
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks: 
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS) 
        
        return img

                   

    # Method to Find the List of Positions Values for the Landmarks

    def findPosition(self, img, handNo = 0, draw = True): 

        lml_List = []
        self.imageheight, self.imagewidth, self.imagechannels = img.shape

        if self.results.multi_hand_landmarks:

            my_hand = self.results.multi_hand_landmarks[handNo] 


            for id, ln in enumerate(my_hand.landmark): 

                h, w, c = img.shape
                cx, cy = int(ln.x * w), int(ln.y * h) 
                lml_List.append([id, cx, cy])

        return lml_List
    
    # Function to get finger landmarks
    def get_finger_lmllist(self, img, handNo = 0, draw = True):
        
        lml_list = []
        
        self.imageheight, self.imagewidth, self.imagechannels = img.shape
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
        
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:

            my_hand = self.results.multi_hand_landmarks[handNo]
            
            for id, ln in enumerate(my_hand.landmark):
                
                if id == 4 or id == 8 or id == 12 or id ==16 or id == 20:
                    lml_list.append(ln)
        
        return lml_list
    
    # Function To draw the Tip of fingers
    def drawHands(self, img, lml_list):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # imgRGB = img
        
        for i in range(len(lml_list)):
            cv2.circle(imgRGB, (int(lml_list[i].x * self.imagewidth), int(lml_list[i].y * self.imageheight)), radius=10, color=(0, 0, 255), thickness=-1)
        
        return imgRGB
        
    def is_hand_stable(self):
         for finger, buffer in self.stability_buffer.items():
             if len(buffer) < self.stability_buffer_size:
                 return False
             variance = np.var(buffer, axis=0)
             if variance[0] > self.stability_threshold or variance[1] > self.stability_threshold:
                 return False
         self.isHands_stable = True
         return True
 
    def update_stability_buffer(self, lml_list):
         for i, landmark in enumerate(lml_list):
             if len(self.stability_buffer[i]) >= self.stability_buffer_size:
                 self.stability_buffer[i].pop(0)
             self.stability_buffer[i].append([int(landmark.x * self.imagewidth), int(landmark.y * self.imageheight)])
 
    def left_hand_configure(self, lml_list, img):
        
        # Setting the Hand Correctly
         self.update_stability_buffer(lml_list)
         
         if not self.isHands_stable:
             if not self.is_hand_stable():
                 cv2.putText(img, "Please keep your hand steady", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                 return img
         
         # Assuming lml_list = [Thumb, Index, Middle, Ring, Pinky]
        
        # Initializing the filter
         
         # Configuring Thumb
         if self.leftThumb_config:
             self.iterations += 1  # Increment iterations
             landmark = np.array([int(lml_list[0].x * self.imagewidth), int(lml_list[0].y * self.imageheight)])
             cv2.putText(img, "Please Lift Your Thumb", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
             
             cTime = time.time()
             landmark[0] = self.eurofilter_x.apply_filter(landmark[0], cTime)
             landmark[1] = self.eurofilter_y.apply_filter(landmark[1], cTime)
             
             if self.iterations > 70:
                 if landmark[1] > self.leftThumb:
                     self.leftThumb = landmark[1]
                 
             if self.iterations >= 100:
                 self.iterations = 0
                 self.leftThumb_config = False
                 self.leftIndex_config = True
                 self.eurofilter_x = ef.OneEuroFilter()
                 self.eurofilter_y = ef.OneEuroFilter()
                 return img
             return img
         
         # Configuring Index
         if self.leftIndex_config:
             self.iterations += 1  # Increment iterations
             landmark = np.array([int(lml_list[1].x * self.imagewidth), int(lml_list[1].y * self.imageheight)])
             cv2.putText(img, "Please Lift Your Index Finger", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
             
             cTime = time.time()
             landmark[0] = self.eurofilter_x.apply_filter(landmark[0], cTime)
             landmark[1] = self.eurofilter_y.apply_filter(landmark[1], cTime)
             
             if self.iterations > 70:
                 if landmark[1] > self.leftIndex:
                     self.leftIndex = landmark[1]
                 
             if self.iterations >= 100:
                 self.iterations = 0
                 self.leftIndex_config = False
                 self.leftMiddle_config = True
                 self.eurofilter_x = ef.OneEuroFilter()
                 self.eurofilter_y = ef.OneEuroFilter()
                 return img
             return img
         
         # Configuring Middle
         if self.leftMiddle_config:
             self.iterations += 1  # Increment iterations
             landmark = np.array([int(lml_list[2].x * self.imagewidth), int(lml_list[2].y * self.imageheight)])
             cv2.putText(img, "Please Lift Your Middle Finger", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
             
             cTime = time.time()
             landmark[0] = self.eurofilter_x.apply_filter(landmark[0], cTime)
             landmark[1] = self.eurofilter_y.apply_filter(landmark[1], cTime)
             
             if self.iterations > 70:
                 if landmark[1] > self.leftMiddle:
                     self.leftMiddle = landmark[1]
                 
             if self.iterations >= 100:
                 self.iterations = 0
                 self.leftMiddle_config = False
                 self.leftRing_config = True
                 self.eurofilter_x = ef.OneEuroFilter()
                 self.eurofilter_y = ef.OneEuroFilter()
                 return img
             return img
         
         # Configuring Ring
         if self.leftRing_config:
             self.iterations += 1  # Increment iterations
             landmark = np.array([int(lml_list[3].x * self.imagewidth), int(lml_list[3].y * self.imageheight)])
             cv2.putText(img, "Please Lift Your Ring Finger", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
             
             cTime = time.time()
             landmark[0] = self.eurofilter_x.apply_filter(landmark[0], cTime)
             landmark[1] = self.eurofilter_y.apply_filter(landmark[1], cTime)
             
             if self.iterations > 70:
                 if landmark[1] > self.leftRing:
                     self.leftRing = landmark[1]
                 
             if self.iterations >= 100:
                 self.iterations = 0
                 self.leftRing_config = False
                 self.leftPinky_config = True
                 self.eurofilter_x = ef.OneEuroFilter()
                 self.eurofilter_y = ef.OneEuroFilter()
                 return img
             return img
         
         # Configuring Pinky
         if self.leftPinky_config:
             self.iterations += 1  # Increment iterations
             landmark = np.array([int(lml_list[4].x * self.imagewidth), int(lml_list[4].y * self.imageheight)])
             cv2.putText(img, "Please Lift Your Pinky Finger", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
             
             cTime = time.time()
             landmark[0] = self.eurofilter_x.apply_filter(landmark[0], cTime)
             landmark[1] = self.eurofilter_y.apply_filter(landmark[1], cTime)
             
             if self.iterations > 70:
                 if landmark[1] > self.leftPinky:
                     self.leftPinky = landmark[1]
                 
             if self.iterations >= 100:
                 self.iterations = 0
                 self.leftPinky_config = False
                 self.leftHand_config = True
                 self.eurofilter_x = ef.OneEuroFilter()
                 self.eurofilter_y = ef.OneEuroFilter()
                 return img
             return img
    
    
    def isIndex(self, landmarkA):
        
        landmarkA.y = int(landmarkA.y * self.imageheight)
        if landmarkA.y < self.leftIndex:
            return True
        else:
            return False 
        
    def isThumb(self, landmarkA):
        
        landmarkA.y = int(landmarkA.y * self.imageheight)
        if landmarkA.y < self.leftThumb:
            return True
        else:
            return False 
        
    def isMiddle(self, landmarkA):
        
        landmarkA.y = int(landmarkA.y * self.imageheight)
        if landmarkA.y < self.leftMiddle:
            return True
        else:
            return False 
        
    def isRing(self, landmarkA):
        
        landmarkA.y = int(landmarkA.y * self.imageheight)
        if landmarkA.y < self.leftRing:
            return True
        else:
            return False 
    
    def isPinky(self, landmarkA):
        
        landmarkA.y = int(landmarkA.y * self.imageheight)
        if landmarkA.y < self.leftPinky:
            return True
        else:
            return False
        
def main():
    
    cap = cv2.VideoCapture(0)
    hand_motion_detector = HandDetector()
    
    index_taps = 0
    start_timer = 0
    index_flag = 0
    final_no_of_taps = 0
    
    while True:
        
        success, img = cap.read()
        finger_list = hand_motion_detector.get_finger_lmllist(img)
        if len(finger_list) != 0:
            img = hand_motion_detector.drawHands(img, finger_list)
            if not hand_motion_detector.leftHand_config:
                img = hand_motion_detector.left_hand_configure(finger_list, img)
        
        
        # if hand_motion_detector.leftHand_config == True:
        #     break
        
        cv2.imshow("IMAGE", img)
        cv2.waitKey(1)
        
    
    while True:
        
        success, img = cap.read()
        finger_list = hand_motion_detector.get_finger_lmllist(img)
        
        
        cv2.putText(img, f"Index_taps = {index_taps}", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
        cv2.putText(img, f"Final_Index_taps = {final_no_of_taps}", (20, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)

        if hand_motion_detector.isIndex(finger_list[1]):
            index_flag = 1
            if start_timer == 0:
                start_timer = time.time()
            
        else:
            if index_flag == 1:
                index_taps += 1
                index_flag = 0
        
        cTime = time.time()
        elapsed_time = cTime - start_timer
        if elapsed_time > 10:
            start_timer = 0
            if index_taps != 0:
                final_no_of_taps = index_taps
            index_taps = 0
    
            
                
        
        cv2.imshow("ANNOTATED IMAGE", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
        
if __name__ == "__main__":
    main()
    
    
