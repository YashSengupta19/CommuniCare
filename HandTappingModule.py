import cv2
from ultralytics import YOLO
import supervision as sv
import time

class HandTappingModule():
    
    def __init__(self):  
        self.model = YOLO("best.pt") # Uses the yolov8 model trained on custom dataset
        self.start_time = 0
        self.tapCount = 0
        self.handLiftedFlag = False
        
    
    # Function to make the predictions
    def make_prediction(self, image): 
        className = "No Detection"
        results = self.model.predict(source=image, conf=0.5)[0]
        detections = sv.Detections.from_ultralytics(results)
        
        for _, _, _, classID, _, _ in detections:
            className =self. model.model.names[classID]
            
        return className
    
        
    # Function to detect whether the hand is lifted or not
    def detectHandLifted(self, classId):
        if classId == "HandLifted":
            return True
        else:
            return False
        
    
    def detectHandFlat(self, classId):
        if classId == "FlatHand":
            return True
        else:
            return False
        
    # Function to detect whether we tapped or not
    # Hand->Lifted->Flat implies 1 tap
    def detectTap(self, classId):
        
        temp_tapCount = None
        
        if self.start_time == 0:
           self.start_time = time.time()
           
        cTime = time.time()
        elapsed_time = cTime - self.start_time
        
        if elapsed_time >= 10:
           self.start_time = 0
           temp_tapCount = self.tapCount
           self.tapCount = 0
           return temp_tapCount
           
        if self.detectHandLifted(classId):
           self.handLiftedFlag = True
        
        if self.handLiftedFlag:
            if self.detectHandFlat(classId):
                self.tapCount += 1
                self.handLiftedFlag = False
        
        return temp_tapCount
    
    
        
def main():
    
    cap = cv2.VideoCapture(0)
    
    
    hand_tap_tracker = HandTappingModule()
    
    box_annotator = sv.BoxAnnotator(thickness = 2,
                                    text_thickness = 3,
                                    text_scale = 1)
    
    finaltapCount = 0
    
    while True:
        
        className = "NoDetection"
        success, frame = cap.read()
        
        
        results = hand_tap_tracker.model.predict(source=frame, conf=0.5)[0]
        
        # Convert the YOLOv8 results into supervision detections
        detections = sv.Detections.from_ultralytics(results)
        
        # print(detections)
        labels = [
            f"{hand_tap_tracker.model.model.names[classid]} {confidence:0.2f}"
            for _, _, confidence, classid, _, _ # Unpacking detections
            in detections
            ]
        
        
        frame = box_annotator.annotate(frame, detections, labels)
        
        for _, _, _, classID, _, _ in detections:
            className = hand_tap_tracker.model.model.names[classID]
            
            
        tapCount = hand_tap_tracker.detectTap(className)
        
        if tapCount != None:
            finaltapCount = tapCount
        
        # print(frame.shape)
        # frame.shape = (480, 640)
        
        cv2.putText(frame, f"TapCount: {finaltapCount}", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
        cv2.imshow("yolov8", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    
    
    
if __name__ == "__main__":
    main()