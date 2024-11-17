import cv2
import mediapipe as mp
import numpy as np
import time

# Used for configuring the eye threshold values
class Configure():
    
    def __init__(self):
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Range of threshold values
        self.eye_closed = [float('inf'), float('-inf')]
        self.eye_open = [float('inf'), float('-inf')]
        self.left = float('-inf')
        self.right = float('inf')
        self.up =  float('-inf')
        self.down = float('inf')
        
        self.iterations = 0
        
        # Creating an instance of FaceMesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, 
                                                    refine_landmarks=True, min_detection_confidence=0.5,
                                                    min_tracking_confidence=0.5)
        
        # Flags which tell which value to configure
        self.eye_open_config = True
        self.eye_closed_config = False
        self.left_config = False
        self.right_config = False
        self.up_config = False
        self.down_config = False
        
    # Get the landmarks of the face using FaceMesh
    def get_landmarks(self, image):
        
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(imageRGB)
        
        self.imageheight, self.imagewidth, self.imagechannels = image.shape
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
        else:
            landmarks = []
            
        return results, landmarks
    
    # Configures the eye values when the eyes are open
    def configure_eye_open(self, landmarkA, landmarkB):
        self.iterations += 1  # Increment iterations
        
        landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
        landmarkB = np.array([int(landmarkB.x * self.imagewidth), int(landmarkB.y * self.imageheight)])
        
        distance = int(np.linalg.norm(landmarkA - landmarkB))
        
        if distance < self.eye_open[0]:
            self.eye_open[0] = distance
        elif distance > self.eye_open[1]:
            self.eye_open[1] = distance
        
        if self.iterations >= 100:
            self.iterations = 0
            self.eye_open_config = False
            self.eye_closed_config = True
            return True
        return False
    
    # Configures the eye values when the eyes are closed
    def configure_eye_closed(self, landmarkA, landmarkB):
        self.iterations += 1  # Increment iterations
        
        landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
        landmarkB = np.array([int(landmarkB.x * self.imagewidth), int(landmarkB.y * self.imageheight)])
        
        distance = int(np.linalg.norm(landmarkA - landmarkB))
        
        if distance < self.eye_closed[0]:
            self.eye_closed[0] = distance
        elif distance > self.eye_closed[1] and distance < self.eye_open[0]:
            self.eye_closed[1] = distance
        
        if self.iterations >= 100:
            self.iterations = 0
            self.eye_closed_config = False
            self.left_config = True
            return True
        return False
    
    
    # Configures the eye values when the we look at the left
    def configure_eye_left(self, landmarkA):
        self.iterations += 1  # Increment iterations
        
        landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
        
        if self.iterations > 70:
            if landmarkA[0] > self.left:
                self.left = landmarkA[0]
            
        if self.iterations >= 100:
            self.iterations = 0
            self.left_config = False
            self.right_config = True
            return True
        return False
    
    
    # Configures the eye values when we look at right
    def configure_eye_right(self, landmarkA):
        self.iterations += 1  # Increment iterations
        
        landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
        
        if self.iterations > 70:
            if landmarkA[0] < self.right:
                self.right = landmarkA[0]
            
        if self.iterations >= 100:
            self.iterations = 0
            self.right_config = False
            self.up_config = True
            return True
        return False
    
    
    # Configures the eye values when we are looking up
    def configure_eye_up(self, landmarkA):
        self.iterations += 1  # Increment iterations
        
        landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
        
        if self.iterations > 70:
            if landmarkA[1] > self.up:
                self.up = landmarkA[1]
            
        if self.iterations >= 100:
            self.iterations = 0
            self.up_config = False
            self.down_config = True
            return True
        return False
    
    
    # Configures the eye values when we are looking down
    def configure_eye_down(self, landmarkA):
        self.iterations += 1  # Increment iterations
        
        landmarkA = np.array([int(landmarkA.x * self.imagewidth), int(landmarkA.y * self.imageheight)])
        
        if self.iterations > 70:
            if landmarkA[1] < self.down:
                self.down = landmarkA[1]
            
        if self.iterations >= 100:
            self.iterations = 0
            self.down_config = False
            return True
        return False

        
        

def main():
    cap = cv2.VideoCapture(0)
    config = Configure()
    pTime = 0
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read frame from camera. Exiting...")
            break
        
        img = cv2.resize(img, (1000, 1000))
        img = cv2.flip(img, 1)
        
        results, landmarks = config.get_landmarks(img)
        if landmarks:
            
            if config.eye_open_config:
                cv2.putText(img, "Please Keep Your Eyes Open", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                done = config.configure_eye_open(landmarks[160], landmarks[144])
                if done:
                    continue
                
            elif config.eye_closed_config: 
                cv2.putText(img, "Please Close Your Eyes", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                done = config.configure_eye_closed(landmarks[160], landmarks[144])
                if done:
                    continue
            
            elif config.left_config:
                cv2.putText(img, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(img, (20, int(config.imageheight / 2)), 20, (0, 0, 255), -1)

                done = config.configure_eye_left(landmarks[469])
                if done:
                    continue
            
            elif config.right_config:
                cv2.putText(img, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(img, (int(config.imagewidth - 20), int(config.imageheight / 2)), 20, (0, 0, 255), -1)
                done = config.configure_eye_right(landmarks[469])
                if done:
                    continue
                
            elif config.up_config:
                cv2.putText(img, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(img, (int(config.imagewidth / 2), 20), 20, (0, 0, 255), -1)
                done = config.configure_eye_up(landmarks[469])
                if done:
                    continue
                
            elif config.down_config:
                cv2.putText(img, "Please Follow The Dot", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
                cv2.circle(img, (int(config.imagewidth / 2), int(config.imageheight - 20)), 20, (0, 0, 255), -1)
                done = config.configure_eye_down(landmarks[469])
                if done:
                    continue
            
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        cv2.putText(img, f'FPS: {int(fps)}', (20, 80), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        pTime = cTime
        
        cv2.imshow("ANNOTATED IMAGE", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    print(config.eye_closed)
    print(config.eye_open)
    print(config.left)
    print(config.right)
    print(config.up)
    print(config.down)
    
    
    

if __name__ == "__main__":
    main()
