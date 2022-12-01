#!/usr/bin/env python

import roslib
# roslib.load_manifest('enph353_ros_lab')
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError
import numpy as np

LOWER_WHITE = np.array([0,0,86], dtype=np.uint8)
UPPER_WHITE = np.array([127,17,206], dtype=np.uint8)
# LOWER_WHITE = np.array([96,0,70], dtype=np.uint8)
# UPPER_WHITE = np.array([125,82,200], dtype=np.uint8)

COL_CROP_RATIO = 5/8
ROW_RATIO = 3/8
MIN_AREA = 7000
MAX_AREA = 27000


class license_detector:

    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/R1/pi_camera/image_raw",Image,self.image_callback)
        

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        rows = cv_image.shape[0]
        cols = cv_image.shape[1]

        processed_img = self.process_image(cv_image)
        split = cv2.split(processed_img)[2]
        blur = cv2.blur(split,(9,9))
        thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY)[1]
        # img_val = cv2.split(processed_img)[2]
        # blur = cv2.blur(img_val,(7,7))
        crop = thresh[int(2/5*rows):int(4/5*rows), 0:cols]
        contours, hierarchy = cv2.findContours(crop, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        c = max(contours, key = cv2.contourArea)
        if len(contours) > 0 and cv2.contourArea(c) < MAX_AREA and cv2.contourArea(c) > MIN_AREA:

            # only display if it is a big enough area
            # print(cv2.contourArea(c))
            
            cv2.drawContours(cv_image, [c], 0, (0,0,255), 3)
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, peri*0.1, True)
            print(approx)
            cv2.drawContours(cv_image, [approx], 0, (0, 255, 0), 3)

        cv2.imshow('image', cv_image)
        cv2.imshow('blur',crop)
        cv2.waitKey(3)
        # This method should just get the image and call other functions
    
    def process_image(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)
        res = cv2.bitwise_and(image,image, mask= mask)
        
        return res
    