'''
Created on 30 Apr 2013

@author: lewy
'''

import signal
import sys
import time
import random
import thread
import pygame
import struct
import socket

class SCALER(object):
    def __init__(self, scale_val):
        self.scale_val = scale_val
        
    def scale(self, val):
        return round(self.scale_val * val)
    
class UDPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def sendPackage(self, package):
        self.sock.sendto(package, (self.host, self.port))

    def setupRcv(self):
        self.sock.bind((self.host, self.port))

    def receivePackage(self):
        data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        return data

class GAMEPAD_REMOT():
    '''
    classdocs
    '''
    
    PRODUCER = 0
    CONSUMER = 1

    udp_port   = 1245
    target_ip  = "192.168.0.10"

    class Packetyzer(object):
        
        @staticmethod
        def packJayData(axes, buttoms):
            return struct.pack('bbbb', axes[0], axes[1], axes[2], axes[3])
    
        @staticmethod
        def unpackJayData(data):
            structdata = struct.unpack('bbbb', data)
            axes = [0,0,0,0]
            if len(structdata) == 4:
                axes[0] = structdata[0]
                axes[1] = structdata[1]
                axes[2] = structdata[2]
                axes[3] = structdata[3]
            return axes
    
    def __init__(self, type=PRODUCER, port=udp_port, host=target_ip, callback=None):
        
        '''
        Constructor
        '''
        self.udp_port = port
        self.target_ip = host
        self.scaler = SCALER(10)
        self.udp = UDPServer(self.target_ip, self.udp_port)
        self.debug_prod = False
        self.callback = callback
        
    def getAxesValues(self):
        self.axes = []
        self.axes.append(self.scaler.scale(self.joy.get_axis(0)))
        self.axes.append(self.scaler.scale(self.joy.get_axis(1)))
        self.axes.append(self.scaler.scale(self.joy.get_axis(2)))
        self.axes.append(self.scaler.scale(self.joy.get_axis(3)))

    def producerProcess(self):
        
        while self.producer_keep_going:
                pygame.event.wait()
                self.getAxesValues()
                self.data_to_send = self.Packetyzer.packJayData(self.axes, 12)
                self.udp.sendPackage(self.data_to_send)
                pygame.event.clear()
                time.sleep(.02)
    
    def consumerProcess(self):
        while self.consumer_keep_going:
            data = self.Packetyzer.unpackJayData(self.udp.receivePackage())
            self.axes = []
            self.axes.append(data[0])
            self.axes.append(data[1])
            self.axes.append(data[2])
            self.axes.append(data[3])
            if self.callback != None: 
                self.callback(self.axes)
                
    def signal_handler(self, signal, frame):
        self.debug_prod = True
        self.producer_keep_going = False
        self.consumer_keep_going = False
        
    def producerStart(self):
        print "Start Producer"
        
        self.producer_keep_going = True
        signal.signal(signal.SIGINT, self.signal_handler)

        try:
            pygame.init()
            pygame.joystick.init()
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
        except:
            print "Couldnt find any joystick"
            return False
        
        print 'Initialized Joystick : %s' % self.joy.get_name()
        thread.start_new_thread(self.producerProcess, ())

        signal.pause()
        while self.producer_keep_going:
            pass
        
        sys.exit()

    def consumerStart(self):
        print "Start Consumer"
        self.udp.setupRcv()
        thread.start_new_thread(self.consumerProcess, ())
        
        self.consumer_keep_going = True
        signal.signal(signal.SIGINT, self.signal_handler)

        signal.pause()
        while self.producer_keep_going:
            pass
        
        sys.exit()

def Ble(axes):
    print "Axes ", axes
    
if __name__ == "__main__":
    
    if sys.argv[1] == "P":
        print "Producer"
        gamepad = GAMEPAD_REMOT(GAMEPAD_REMOT.PRODUCER, host="127.0.0.1")
        if True == gamepad.producerStart():
            while True:
                time.sleep(1)
                print "PRODUCER = %d" %(random.randrange(10))
    else:
        print "Consumer"
        gamepad = GAMEPAD_REMOT(GAMEPAD_REMOT.CONSUMER, host="127.0.0.1", callback=Ble)
        gamepad.consumerStart()
