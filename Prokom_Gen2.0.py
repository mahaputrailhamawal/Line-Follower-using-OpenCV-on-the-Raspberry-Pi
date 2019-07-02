from gpiozero import DistanceSensor
from RPi import GPIO
from urllib.request import urlopen
from time import sleep
import os
import serial
import threading
import cv2
import numpy as np
import math
import socket
from camera1 import VideoCamera
from flask import Flask, render_template, Response

app = Flask(__name__)

distance = 0
temp = 0
speed = "0"
manual_speed = "0"
direction = "maju"
mode = "auto"
rotation = 0
rpm = 0
read = ""

TCP_IP = '192.168.1.69'
TCP_PORT = 5005

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
arduino = serial.Serial('/dev/ttyACM0',9600, timeout = 5)
ultrasonic = DistanceSensor(echo = 21, trigger = 20, max_distance = 2.0)
camera = cv2.VideoCapture(0)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clkLastState = GPIO.input(17)

def commandArduino():
    arduino.close()
    arduino.open()
    while True:
        command = "#" + direction + "#" + speed + "#" + speed + "#q"        
        command = str.lower(command)
        arduino.write(command.encode())
        print(command)
        
def controlMode():
    while True:
        global speed
        global distance
        distance = int(ultrasonic.distance * 100)
        
        if(mode == "auto"):
            if(distance >= 50):
                speed = "255"
            else:
                speed = "0"
        else:
            speed = manual_speed

        readEncoder()

def readEncoder():
    global rotation
    global clkLastState
    clkState = GPIO.input(17)
    if clkState != clkLastState:
        if clkState:
            rotation += 0.05

    clkLastState = clkState

def readRPM():
    while True:
        global rpm
        global rotation
        sleep(3)
        rpm = int(rotation * 20)
        rotation = 0

def sendDataServer():
    while True:
        temp = os.popen('vcgencmd measure_temp').readline()
        temp = float(temp.replace("temp=","").replace("'C",""))
        
        urlopen("http://192.168.1.2/ceabot/add_data.php?jarak=" + str(distance) + "&suhu=" + str(temp) + "&kecepatan=" + str(rpm)).read()
        sleep(2)
        
def tcpServer():
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen(1)
    conn, addr = sock.accept()
    while True:
        global mode
        global direction
        global manual_speed

        data = conn.recv(20)
        data = data.decode("utf-8")
        length = len(data)

        tcp_data = data.split("#") 
        if(length >= 13):
            direction = str(tcp_data[0])      
            manual_speed = str(tcp_data[1])
            mode = str(tcp_data[2])
        else:
            direction = "maju"      
            manual_speed = "0"
            mode = "auto"
def gen():
    while True:
        frame = camera.get_image()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


mode_thread = threading.Thread(target = controlMode)
mode_thread.daemon = True
mode_thread.start()

command_thread = threading.Thread(target = commandArduino)
command_thread.daemon = True
command_thread.start()

database_thread = threading.Thread(target = sendDataServer)
database_thread.daemon = True
database_thread.start()

vision_thread = threading.Thread(target = gen)
vision_thread.daemon = True
vision_thread.start()

rpm_thread = threading.Thread(target = readRPM)
rpm_thread.daemon = True
rpm_thread.start()

tcp_thread = threading.Thread(target = tcpServer)
tcp_thread.daemon = True
tcp_thread.start()

@app.route('/')
def index():
    return render_template('index1.html')        

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                  mimetype='multipart/x-mixed-replace; boundary=frame')

#if __name__ == '__main__':
    #app.run(host='192.168.1.69', port=5000, debug=True)
