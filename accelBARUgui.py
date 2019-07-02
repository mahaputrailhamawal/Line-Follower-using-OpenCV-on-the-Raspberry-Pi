from PyQt5 import QtCore, QtGui, QtWidgets, uic
# import accelero
import socket
import queue, sys, threading, time, random
import numpy as np
import cv2
import re
import RPi.GPIO as GPIO
import socket
from urllib.request import urlopen
from sense_hat import SenseHat
from time import sleep
sense = SenseHat()
sense.set_imu_config(False, True, False)
dataSensor=120
dire = "maju"
tipe= "auto"
running = False
capture_thread = None
form_class = uic.loadUiType("GUImatataumanual.ui")[0]
q = queue.Queue()
param = 0
        ################### Connection ###################
def conn():
    TCP_IP = '192.168.1.69'
    TCP_PORT = 5005

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP,TCP_PORT))
    while True:
        MESSAGE = ( dire + "#" + str(dataSensor) + "#" + tipe).encode('utf-8')
        #MESSAGE = "coba".encode('utf-8')
        print(MESSAGE)
        s.send(MESSAGE)
        time.sleep(0.1)
        
        ################### VIDEO STREAMING ###################
def grab(cam, queue, width, height, fps):
    global running
    url = 'http://192.168.43.38:5000/stream/video_feed.mjpg'
    stream = urlopen(url)                                               
        
    # Read the boundary message and discard
    stream.readline()

    sz = 0
    rdbuffer = None

    clen_re = re.compile(b'Content-Length: (\d+)\\r\\n')

    while(running):
        stream.readline()                    # content type
    
        try:                                 # content length
            m = clen_re.match(stream.readline()) 
            clen = int(m.group(1))
        except:
            stream.readline()                    # timestamp
            stream.readline()                    # empty line
        
        # Reallocate buffer if necessary
        if clen > sz:
            sz = clen*2
            rdbuffer = bytearray(sz)
            rdview = memoryview(rdbuffer)
        
        # Read frame into the preallocated buffer
        stream.readinto(rdview[:clen])
        
        stream.readline() # endline
        stream.readline() # boundary
        
        frame = {}
        img = cv2.imdecode(np.frombuffer(rdbuffer, count=clen, dtype=np.byte), flags=cv2.IMREAD_COLOR)
        frame["img"] = img

        if queue.qsize() < 10:
            queue.put(frame)
        else:
            print(queue.qsize())

        ################### IMAGE WIDGET ###################
class OwnImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()


class MyWindowClass(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        ################### START BUTTON ###################
        self.startButton_2.clicked.connect(self.start_clicked)
      

      
        self.startShadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.startShadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.startShadow.setXOffset(0)
        self.startShadow.setYOffset(2)
        self.startShadow.setBlurRadius(12)
        self.startButton_2.setGraphicsEffect(self.startShadow)

        self.window_width = self.ImgWidget.frameSize().width()
        self.window_height = self.ImgWidget.frameSize().height()
        self.ImgWidget = OwnImageWidget(self.ImgWidget)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start()
        # self.show = QtCore.QTimer(self)
        # self.show.timeout.connect(self.showAccelero)
        # self.show.start()
        
        if self.startButton_2.isDown() == False:
            self.KONDISI.setVisible(False)

        ################### ACCELERO ###################
        #mengubah arah robot untuk berbelok ke kiri atau ke kanan
    def tampil(self):
        global dire
        def calculate() :
            o = sense.get_orientation()
            data = round(o["yaw"], 2)
            if data > 180 :
                return (data - 360)
            else :
                return data
    
        def drive(val):
            if val < 15 and val > -15:
                dire = "maju"
            elif val > 15 :
                dire = "kiri"
            else :
                dire = "kana"
            
            return dire

        while True :
            val = calculate()
            dire = drive(val)
            if dire=="kana":
                self.KONDISI.setText("kanan")
            else :
                self.KONDISI.setText(dire)
            self.DATA.setText("%f"%calculate())
    #mengatur kecepatan dari robot untuk bergerak
    def maju(self) :
        global dataSensor
        if dataSensor + 10 <= 255:
            dataSensor = dataSensor + 10
        else:
            dataSensor = 255
        self.kecepatan.setText("%d"%dataSensor)
    def maju2(self) :
        global dataSensor
        if dataSensor + 25 <= 255:
            dataSensor = dataSensor + 25
        else:
            dataSensor = 255
        self.kecepatan.setText("%d"%dataSensor)
    def mundur1(self) :
        global dataSensor
        if dataSensor - 10 >= 0:
            dataSensor = dataSensor - 10
        else:
            dataSensor = 0
        self.kecepatan.setText("%d"%dataSensor)
    def mundur2(self) :
        global dataSensor
        if dataSensor - 25 >= 0:
            dataSensor = dataSensor - 25
        else:
            dataSensor = 0
        self.kecepatan.setText("%d"%dataSensor)
    def berhenti(self) :
        global dataSensor
        dataSensor = 0
        self.kecepatan.setText("%d"%dataSensor)
    #memilih mode untuk menjalankan robot auto atau manual
    def manual1(self) :
        global tipe
        tipe = "manual"
        self.tipe.setText("MANUAL")
    def auto(self) :
        global tipe
        tipe = "auto"
        self.tipe.setText("AUTO")
    #fungsi dari start button untuk memulai demo dari robot yang dibuat
    def start_clicked(self):
        global running
        running = True
        self.nambah.clicked.connect(self.maju)
        self.manual.clicked.connect(self.manual1)
        self.startButton_4.clicked.connect(self.auto)
        self.nambah_2.clicked.connect(self.maju2)
        self.mundur.clicked.connect(self.mundur1)
        self.mundur_2.clicked.connect(self.mundur2)
        self.stop.clicked.connect(self.berhenti)
        self.thread1= threading.Thread(target=self.tampil)
        self.thread1.daemon = True
        self.thread1.start()
        
        thread2= threading.Thread(target=conn)
        thread2.daemon = True
        thread2.start()
        
        #capture_thread.start()
        self.startButton_2.setEnabled(False)
        self.startButton_2.setText('Starting...')
        self.KONDISI.setVisible(True)

    def update_frame(self):
        if not q.empty():
            self.startButton_2.setText('Camera is live')
            frame = q.get()
            img = frame["img"]

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1

            img = cv2.resize(img, None, fx=scale, fy=scale,
                             interpolation=cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height,
                                 bpl, QtGui.QImage.Format_RGB888)
            self.ImgWidget.setImage(image)

    def closeEvent(self, event):
        global running
        running = False

#capture_thread = threading.Thread(target=grab, args=(0, q, 1920, 1080, 30))
app = QtWidgets.QApplication(sys.argv)
w = MyWindowClass(None)
w.setWindowTitle('FORMULA PI')
w.show()

app.exec_()
