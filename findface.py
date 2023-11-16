import cv2
import torch
import numpy as np
from ultralytics import YOLO

class FaceTrack():
    
    ''' Load YOLOv5 model
    - load()에 매개변수로 'yolov5 폴더 저장된 위치', 'custom', path = 'train된 모델', source = 'local' 순으로 와야한다.
    model = torch.hub.load('C://Users//k7403//Desktop//ProjectPython//yolov5-master', 'custom', path ='models/best.pt', source='local')
    '''
    # Load YOLOV8 model
    model = YOLO('yolov8n.pt')
    
    w, h = 360, 240
    fbRange = [6200, 6800]
    pid = [0.4, 0.4, 0]
    pError = 0

    def find_Face(self, frame):
        
        # detected object's valuable array
        myFaceListC = []
        myFaceListArea = []

        # Perform object detection with the YOLOv5 model
        results = self.model(frame)
        
        # Get detected objects
        detected_objects = results.pred[0]
            
        for obj in detected_objects:
            # Extract bounding box coordinates
            x1, y1, x2, y2, conf, cls = obj.tolist()
                
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            area = (x2-x1) * (y2-y1)
                
            # Draw a rectangle around the detected object
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                
            # Calculate and print the center coordinates

            print(f"Object center coordinates: ({center_x}, {center_y})")
            myFaceListC.append([center_x,center_y])
            myFaceListArea.append(area)
            
            if len(myFaceListArea) != 0:
                i = myFaceListArea.index(max(myFaceListArea)) # 카메라를 통해 얻은 얼굴 값(리스트)중 그 면적이 제일 큰, 즉 제일 가까운 얼굴
                return frame, [myFaceListC[i],myFaceListArea[i]]
            else:
                return frame, [[0, 0], 0]
            
            
    def trackFace(self, info, w, pid, pError):
        area = info[1] # 가장 가까운 얼굴 면적
        x, y = info[0] # 가장 가까운 얼굴 중앙 좌표값
        fb = 0

        error = x - w // 2 # 얼굴의 x 좌표 값이 중앙으로부터 얼마나 떨어져 있는가 편차
        speed = pid[0]*error + pid[1]*(error-pError)
        speed = int(np.clip(speed, -100, 100))

        if area > self.fbRange[0] and area < self.fbRange[1]: # 드론이 6200에서 6800사이에 있는 경우 정지
            fb = 0
        elif area> self.fbRange[1]:
            fb = -20
        elif area < self.fbRange[0] and area != 0: #만약 앞에 아무도 없다면 area는 0이고 직진만 할 것이다
            fb = 20


        if x == 0:
            speed = 0 
            error = 0

        #print(speed, fb)
        me.send_rc_control(0, fb, 0, speed)
        return error