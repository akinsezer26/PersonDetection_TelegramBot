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
        self.cap = cv2.VideoCapture(source)

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

        time.sleep(interval)

        try:
            for i in range(24):
                self.cap.grab()

            ret,image = self.cap.read()

            if(cv2.countNonZero(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))==0):
                return False, "Resim Siyah"
            else:
                image_copy = image.copy()
                ##################################### Masking ############################################
                marginx = 215
                marginy = 0

                cv2.rectangle(image_copy, (0+marginx,0+marginy), (50+marginx, 76+marginy), (255,0,255),-1)
                cv2.rectangle(image_copy, (50+marginx,0+marginy), (100+marginx, 65+marginy), (255,0,255),-1)   #CAM1
                cv2.rectangle(image_copy, (100+marginx,0+marginy), (150+marginx, 50+marginy), (255,0,255),-1)
                cv2.rectangle(image_copy, (150+marginx,0+marginy), (210+marginx, 40+marginy), (255,0,255),-1)

                cv2.rectangle(image_copy, (140,420), (212, 480), (255,0,255),-1)  #CAM7

                ##################################### Masking ############################################
                
                image_dn = self.array_to_image(image_copy)
                dn.rgbgr_image(image_dn)

                hour = datetime.datetime.now().hour
                dn.nnp_initialize()
                r = None

                #print("inceleniyor")

                if(hour > 7 and hour < 18):
                    r = dn.detect(self.net, self.meta, image_dn, 0.35)
                else:
                    r = dn.detect(self.net, self.meta, image_dn, 0.30)

                length = len(r)

                #print(r)

                flag = False
                if(length>0):
                    self.DetectedImage = image
                for i in range(length):
                    if(str(r[i][0]).find("person") >= 0):
                        self.DetectedImage = cv2.rectangle(self.DetectedImage, (int(r[i][2][0]) - int(r[i][2][2]) -5, int(r[i][2][1]) - int(r[i][2][3])-5), (int(r[i][2][0]) + int(r[i][2][2]) +5, int(r[i][2][1]) + int(r[i][2][3])+5), (255,0,255), 2)
                        #print("Detected")
                        flag = True

                return flag, r
        except:
            #print("error")
            return False, "Usb Takili Degil"
