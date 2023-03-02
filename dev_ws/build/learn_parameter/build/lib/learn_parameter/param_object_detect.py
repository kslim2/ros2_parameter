#!usr/bin/env python3 

import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Image 
from cv_bridge import CvBridge 
import cv2 
import numpy as np 

lower_red = np.array([0, 90, 128])
upper_red = np.array([180, 255, 255])

class ImageSubscriber(Node):

    def __init__(self, name):
        super().__init__(name)
        self.sub = self.create_subscription(Image, "image_raw", 
            self.listener_callback, 10)
        self.cv_bridge = CvBridge()
        self.declare_parameter("red_h_upper", 0)
        self.declare_parameter("red_h_lower", 0)

    def object_detect(self, image):
        upper_red[0] = self.get_parameter('red_h_upper').get_parameter_value().\
            integer_value 
        lower_red[0] = self.get_parameter("red_h_lower").\
            get_parameter_value().integer_value 
        
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(hsv_img, lower_red, upper_red)
        contours, hierarchy = cv2.findContours(mask_red, cv2.RETR_LIST, 
            cv2.CHAIN_APPROX_NONE)
        
        for cnt in contours:
            if cnt.shape[0] < 150:
                continue 

            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.drawContours(image, [cnt], -1, (0, 255, 0), 2)
            cv2.circle(image, (int(x+w/2), int(y+h/2)), 5, 
                (0, 255, 0), -1)
        
        cv2.imshow("object", image)
        cv2.waitKey(50)

    def listener_callback(self, data):
        self.get_logger().info("Receiving video frame")
        image = self.cv_bridge.imgmsg_to_cv2(data, "bgr8")
        self.object_detect(image)

def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriber("param_object_detect")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
        