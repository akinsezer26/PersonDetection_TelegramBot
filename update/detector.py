import sys, os
import cv2
import numpy as np
import time
import datetime
import yolov5
import math

class yoloHandler:

    def __init__(self, source):
        self.DetectedImage = None
        self.cap = cv2.VideoCapture(source)
        self.cap.set(3, 1920)
        self.cap.set(4, 1080)
        self.model = yolov5.load('/home/akin/guvenlik/yolov5s.pt')
        self.model.conf = 0.55

    def yolo_detect(self,interval):

        time.sleep(interval)

        try:
            #for i in range(24):
            #    self.cap.grab()

            ret,image = self.cap.read()

            cam1 = image[0:360, 0:640]
            cam2 = image[0:360, 640:1280]
            cam3 = image[0:360, 1280:1920]

            cam4 = image[360:720, 0:640]
            cam5 = image[360:720, 640:1280]
            cam6 = image[360:720, 1280:1920]

            cam7 = image[720:1080, 0:640]
            cam8 = image[720:1080, 640:1280]

	    #cam1, cam2, cam4, cam6
            combined_images = np.zeros((720,1280,3), np.uint8)
            combined_images[0:360, 0:640] = cam1
            combined_images[0:360, 640:1280] = cam2
            combined_images[360:720, 0:640] = cam4
            combined_images[360:720, 640:1280] = cam6
            
            image = combined_images
            cv2.rectangle(image, (416, 211), (630, 353), (255, 255, 255), -1)
            cv2.rectangle(image, (528, 112), (630, 264), (255, 255, 255), -1)
            
            if(cv2.countNonZero(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))==0):
                return False, "Resim Siyah"
            else:
                image_copy = image.copy()

                hour = datetime.datetime.now().hour
                r = None

                #print("inceleniyor")

                if(hour > 7 and hour < 18):
                    r = self.model(image_copy)
                else:
                    r = self.model(image_copy)

                results = r.pandas().xyxy[0]
                results = results[results.name == 'person']
                
                flag = False
                length = len(results)

                predictions = list()
                if(length>0):
                    self.DetectedImage = image
                    for i in range(length):
                        x1 = math.floor(results.iloc[i]['xmin'])
                        y1 = math.floor(results.iloc[i]['ymin'])
                        x2 = math.floor(results.iloc[i]['xmax'])
                        y2 = math.floor(results.iloc[i]['ymax'])
                        conf = results.iloc[i]['confidence']
                        cv2.rectangle(self.DetectedImage, (x1, y1), (x2, y2), color = (255,0,255), thickness = 1)
                        predictions.append(('person', conf))
                    flag = True
                
                return flag, predictions
        except:
            #print("error")
            return False, "Usb Takili Degil"
