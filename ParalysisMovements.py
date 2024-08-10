import cv2
import mediapipe as mp
import numpy as np
import time

def calc_distance(landmarkA, landmarkB, image):
    
    imageheight, imagewidth, imagechannels = image.shape
    
    landmarkA = np.array([int(landmarkA.x * imagewidth), int(landmarkA.y * imageheight)])
    landmarkB = np.array([int(landmarkB.x * imagewidth), int(landmarkB.y * imageheight)])
    
    distance = int(np.linalg.norm(landmarkA - landmarkB))
    
    return distance


# Uses the configured values from the Configure.py and uses it to predict various eye movement
class ParalysisMovements():
    
    def __init__(self, eye_closed, eye_open, eye_left_threshold, eye_right_threshold, eye_up_threshold, eye_down_threshold):
        
        self.eye_closed = eye_closed
        self.eye_open = eye_open
        self.eye_down_threshold = eye_down_threshold
        self.eye_up_threshold = eye_up_threshold
        self.eye_left_threshold = eye_left_threshold
        self.eye_right_threshold = eye_right_threshold
        
        self.mp_drawing = mp.solutions.download_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode = True, max_num_faces = 1, 
                                                    refine_landmarks = True, min_detection_confidence = 0.5,
                                                    min_tracking_confidence = 0.5)
        
        self.blink_timer = 0
        self.closed_flag = False
        
    
    # Function to get the landmarks in the FaceMesh
    def get_landmarks(self, image):
    
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        results = self.face_mesh.process(imageRGB)
        
        self.imageheight, self.imagewidth, self.imagechannels = image.shape
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
        else:
            landmarks = []
            
        return results, landmarks
    
    # Compares the eye threshold values to check whether the eyes are closed or not
    def did_close_eyes(self, landmarkA, landmarkB):
         
         landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
         landmarkB = np.array([int(landmarkB.x * self.imagewidth), int(landmarkB.y * self.imageheight)])
         
         distance = int(np.linalg.norm(landmarkA - landmarkB))
         
         if distance < self.eye_open[0]:
             if self.blink_timer == 0:
                 self.blink_timer = time.time()
                 
             else:
                 current_time = time.time()
                 elapsed_time = current_time - self.blink_timer
                 
                 if elapsed_time >= 1:
                     self.closed_flag = True
                     return True
                 else:
                     self.closed_flag = False
                     return False
         # else:
             # self.blink_timer = 0  # Reset blink timer if eyes are not closed
         return False
     
    # Compares the eye threshold values to check whether the eyes are open or not
    def did_open_eyes(self, landmarkA, landmarkB):
        
        landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
        landmarkB = np.array([int(landmarkB.x * self.imagewidth), int(landmarkB.y * self.imageheight)])
        
        distance = int(np.linalg.norm(landmarkA - landmarkB))
        
        if distance > self.eye_closed[1]:
            return True
        
        return False
     
    # Checks if we blinked the eyes or not
    # Eye->Closed->Open after 1 second implies a blink

    def did_Blink(self, landmarkA, landmarkB):
         
        if not self.closed_flag:
            self.did_close_eyes(landmarkA, landmarkB)
        if self.closed_flag:
            x = self.did_open_eyes(landmarkA, landmarkB)
            if x == True:
                self.closed_flag = False
                self.blink_timer = 0
                return True
            
        return False
    
    # Checks if we are looking to left
    def eye_left(self, landmarkA):
        
        landmarkA.x = int(landmarkA.x * self.imagewidth)
        if landmarkA.x < self.eye_left_threshold:
            return True
        else:
            return False
        
    # Checks if we are looking to right
    def eye_right(self, landmarkA):
        
        # landmarkA.x = int(landmarkA.x * self.imagewidth)
        if landmarkA.x > self.eye_right_threshold:
            return True
        else:
            return False
    
    # Checks if we are looking up
    def eye_up(self, landmarkA):
        
        landmarkA.y = int(landmarkA.y * self.imageheight)
        if landmarkA.y < self.eye_up_threshold:
            return True
        else:
            return False  
        
    # Checks if we are looking down
    def eye_down(self, landmarkA):
        
        # landmarkA.y = int(landmarkA.y * self.imageheight)
        if landmarkA.y > self.eye_down_threshold:
            return True
        else:
            return False 
    
    

def main():
    
    cap = cv2.VideoCapture(0)
    
    pm = ParalysisMovements([6, 7], [8, 10], 388, 413, 478, 509)
    
    pTime = 0
    
    blinkCount = 0
    
    
    while True:
        
        
        success, img = cap.read()
        
        if not success:
            print("Failed to read frame from camera. Exiting...")
            break
        
        cv2.putText(img, f'BlinkCount: {int(blinkCount)}', (1, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
        
        results, landmarks = pm.get_landmarks(img)
        
        
        if landmarks:
            
            distance = calc_distance(landmarks[160], landmarks[144], img)
            cv2.putText(img, f'EyeDistance: {int(distance)}', (1, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
            
            
            if pm.did_Blink(landmarks[160], landmarks[144]):
                blinkCount += 1
            
                
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            
            cv2.putText(img, f'FPS: {int(fps)}', (1, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
            pTime = cTime
            
            
            
            cv2.imshow("ANNOTATED IMAGE", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        

        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
        
        
        
        
        
        
        
    