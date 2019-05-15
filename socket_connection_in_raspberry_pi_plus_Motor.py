# -*- coding: utf-8 -*-

import io 
import socket
import struct
import time
import picamera
import argparse
import numpy as np
import RPi.GPIO as GPIO
from gpiozero import DistanceSensor

#Left Motor
motor1A = 16
motor1B = 18

#Right Motor
motor2A = 13
motor2B = 15

#Motor Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor1A,GPIO.OUT)
GPIO.setup(motor1B,GPIO.OUT)
GPIO.setup(motor2A,GPIO.OUT)        
GPIO.setup(motor2B,GPIO.OUT)

#PWM
p1A = GPIO.PWM(motor1A,600)
p1A.start(0)
p1B = GPIO.PWM(motor1B,600)
p1B.start(0)
p2A = GPIO.PWM(motor2A,600)
p2A.start(0)
p2B = GPIO.PWM(motor2B,600)
p2B.start(0)

def forward():
    p1A.ChangeDutyCycle(100)
    p1B.ChangeDutyCycle(0)
    p2A.ChangeDutyCycle(100)
    p2B.ChangeDutyCycle(0)
def backward():
    p1A.ChangeDutyCycle(0)
    p1B.ChangeDutyCycle(100)
    p2A.ChangeDutyCycle(0)
    p2B.ChangeDutyCycle(100)
def turn_left():
    p1A.ChangeDutyCycle(0)
    p1B.ChangeDutyCycle(100)
    p2A.ChangeDutyCycle(100)
    p2B.ChangeDutyCycle(0)
def turn_right():
    p1A.ChangeDutyCycle(100)
    p1B.ChangeDutyCycle(0)
    p2A.ChangeDutyCycle(0)
    p2B.ChangeDutyCycle(100)
def stop() :
    p1A.ChangeDutyCycle(0)
    p1B.ChangeDutyCycle(0)
    p2A.ChangeDutyCycle(0)
    p2B.ChangeDutyCycle(0)
def spiral() :
    p1A.ChangeDutyCycle(100)
    p1B.ChangeDutyCycle(0)
    p2A.ChangeDutyCycle(50)
    p2B.ChangeDutyCycle(0)

parser = argparse.ArgumentParser(description = 'Press IP adress and Port number')
parser.add_argument('-ip', type = str, default = '192.168.0.101')
parser.add_argument('-port', type = int, default = 9999)

a = parser.parse_args()
ip = a.ip
port = a.port   

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))

connection = client_socket.makefile('wb')


# 초음파 센서
front = DistanceSensor(19, 26)

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.vflip = True
        camera.hflip = True
        camera.framerate = 10
        time.sleep(10)
        start = time.time()
        stream = io.BytesIO()

        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            stream.seek(0)
            stream.truncate()
            connection.write(struct.pack('<L', 0))
            data = client_socket.recv(1024)
            print(data)

            distance_front = front.distance

            print('Distance to nearest object is', distance_front, 'm')

            if data == 'forward' :
                forward()
                continue
            elif data == 'backward' :
                backward()
                continue
            elif data == 'turn_left' :
                turn_left()
                continue
            elif data == 'turn_right' :
                turn_right()
                continue
            elif data == 'through' :
                continue
            elif data == 'spiral' :
                spiral()
                continue
            elif data == 'quit' :
                stop()
                break
        GPIO.cleanup()

finally:
    connection.close()
    client_socket.close()
