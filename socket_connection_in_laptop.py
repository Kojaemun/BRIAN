# -*- coding: utf-8 -*-

import datetime
import threading
import SocketServer
import cv2
import numpy as np
import time
import math
import socket



# ip 주소 받아오기
my_ip = socket.gethostbyname(socket.gethostname())
print(my_ip)

# 비디오 녹화 관련
fourcc = cv2.VideoWriter_fourcc(*'XVID')
record = False


detection_result = "No_detection"

class object_detection(object):
    def ball_detection(self, classifier, gray_image, color_image):

        detection_result = "No_detection"

        center = []
        width = []

        balls = classifier.detectMultiScale(image = gray_image, scaleFactor = 1.03, minNeighbors = 2 )

        for (x,y,w,h) in balls :
            cv2.rectangle(color_image, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(color_image, 'BALL', (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            center = center + [(x+w) / 2 , (y+h) / 2]
            width = width + [w]

        if len(balls) > 1 :
            detection_result = 'Multi_detection'
        elif len(balls) == 1 :
            detection_result = 'Single_detection'
        else :
            detection_result = 'No_detection'

        return detection_result, balls, center, width

class VideoStreamHandler(SocketServer.StreamRequestHandler):

    object_detection = object_detection()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    ball_cascade = cv2.CascadeClassifier('190427_HAAR3.xml')

    def handle(self):

        stream_bytes = ''
        self.request.send('forward')
        
        # 한 프레임 씩 이미지를 받아와 Stream
        try:
            while True:
                stream_bytes +=self.rfile.read(1024)

                first = stream_bytes.find('\xff\xd8')

                last = stream_bytes.find('\xff\xd9')

                if first != -1 and last != -1:

                    jpg = stream_bytes[first:last + 2]

                    stream_bytes = stream_bytes[last + 2:]

                    image = cv2.imdecode(np.fromstring(jpg, dtype = np.uint8), cv2.IMREAD_UNCHANGED)

                    # image2 = cv2.GaussianBlur(image, (3,3), 0)

                    image2 = cv2.medianBlur(image,5)


                    gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

                    # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,param1=50,param2=50 ,minRadius=0, maxRadius=0)

                    # if circles is not None:

                    #     circles = np.uint16(np.around(circles))
                        
                    #     for i in circles[0,:]:
                    #         cv2.circle(image2,(i[0],i[1]),i[2],(0,255,0),2)
                    #         cv2.circle(image2,(i[0],i[1]),2,(0,0,255),3)                  

                    
                    # balls = self.object_detection.ball_detection(self.ball_cascade, gray, image2)
                    global record
                    cv2.imshow('image', image2)
                    cv2.imshow('gray', gray)
                    
                    key = cv2.waitKey(1) & 0xFF

                    # print(balls[0])
                    # if balls[0] == 'No_detection' :
                    #     self.request.send('stop')
                    # elif balls[0] == 'Single_detection' :
                    #     self.request.send('forward')
                    # else :
                    #     self.request.send('left')

                    #q 누르면 끝
                    if key == ord('q'):
                        self.request.send('quit')
                        break
                    # c 누르면 녹화 시작
                    elif key == ord('c'):
                       print("Start Capture")
                       record = True
                       writer = cv2.VideoWriter('output.avi', fourcc, 10.0, (640,480))
                    #x 누르면 녹화 종료    
                    elif key == ord('x'):
                       print("Stop Capture")
                       record = False
                       writer.release()

                    if record == True:
                       print("Capture")
                       writer.write(image)                    

            cv2.destroyAllWindows()

        finally:
            print("Connection closed on thread 1")


def select_white(image, white):
    imgHLS = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    white_mask = cv2.inRange(imgHLS, np.array([0,white,0]), np.array([255,255,255]))
    masked_image = cv2.bitwise_and(image , image, mask = white_mask)

    return white_mask, masked_image

class ThreadServer(object):
    def server_thread(host, port):
        server = SocketServer.TCPServer((host, port), VideoStreamHandler)  
        server.serve_forever()

    video_thread = threading.Thread(target=server_thread(my_ip, 8888))
    video_thread.start()



if __name__ == '__main__':

    ThreadServer()




