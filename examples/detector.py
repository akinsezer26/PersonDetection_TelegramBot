import sys, os
path = "/home/pi/darknet/"
sys.path.insert(1, path + 'python')

import darknet as dn
import pdb
import cv2
import numpy as np
import time
import datetime

class yoloHandler:

    def __init__(self, source):
        self.DetectedImage = None
        dn.set_gpu(0)
        self.net = dn.load_net(bytes(path + "cfg/yolov3-tiny.cfg", encoding='utf-8'), bytes(path + "/yolov3-tiny.weights", encoding='utf-8'), 0)
        self.meta = dn.load_meta(bytes(path + "cfg/coco.data", encoding='utf-8'))

    def array_to_image(self, arr):
        arr = arr.transpose(2,0,1)
        c = arr.shape[0]
        h = arr.shape[1]
        w = arr.shape[2]
        arr = (arr/255.0).flatten()
        data = dn.c_array(dn.c_float, arr)
        im = dn.IMAGE(w,h,c,data)
        return im

    def yolo_detect(self,interval):
        cap = cv2.VideoCapture(0)
        time.sleep(interval)
        try:
            #cap = cv2.VideoCapture(0)
            ret,image = cap.read()

            image_dn = self.array_to_image(image)
            dn.rgbgr_image(image_dn)

            hour = datetime.datetime.now().hour
            dn.nnp_initialize()
            r = None
            print("inceleniyor")
            if(hour > 7 and hour < 18):
                r = dn.detect(self.net, self.meta, image_dn, 0.2)
            else:
                r = dn.detect(self.net, self.meta, image_dn, 0.1)

            length = len(r)

            print(r)

            flag = False
            if(length>0):
                self.DetectedImage = image
            for i in range(length):
                if(str(r[i][0]).find("person") >= 0):
                    self.DetectedImage = cv2.rectangle(self.DetectedImage, (int(r[i][2][0]) - int(r[i][2][2]) -5, int(r[i][2][1]) - int(r[i][2][3])-5), (int(r[i][2][0]) + int(r[i][2][2]) +5, int(r[i][2][1]) + int(r[i][2][3])+5), (255,0,255), 2)
                    print("Detected")
                    flag = True

            cap.release()
            return flag
        except:
            print("error")
            return False
