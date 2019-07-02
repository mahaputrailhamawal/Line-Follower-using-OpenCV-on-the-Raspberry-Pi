import math
import cv2
import numpy as np


def getROI(frame):
    upper_left  = (50, 50)
    bottom_right = (1028, 1028)  
    rect_frame = frame[upper_left[1]:bottom_right[1], upper_left[0]:bottom_right[0]]
    return rect_frame

class VideoCamera(object):

    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_image(self):
        theta = 0 
        success, image = self.video.read()
        
        image  = getROI(image)
        gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred=cv2.GaussianBlur(gray,(15,15),0)
        edged=cv2.Canny(blurred,40,120)
        lines=cv2.HoughLinesP(edged,10,np.pi/180,15, 5, 10)
    
        if lines is not None:
            for x in range(0, len(lines)):
                for x1, y1, x2, y2 in lines[x]:
                    cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    theta = theta + math.atan2((y2-y1), (x2-x1))
            
        threshold = 5
        cv2.imshow('hasil',image)
        if(abs(theta) < threshold):
            direction = "maju"
        elif(theta > threshold):
            direction = "kiri"
        elif(theta < -threshold):
            direction = "kana"
 
#        cv2.imshow("image", image)
#        cv2.imshow("mask", mask)
        theta = 0
        ret, jpeg = cv2.imencode('.jpg', image)
        
        return jpeg.tobytes()

