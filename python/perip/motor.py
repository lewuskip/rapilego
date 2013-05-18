'''
Created on 4 Mar 2013

@author: lewy
'''

import time
import serial

class MOTOR:
    def __init__(self, device):
        self.ser = serial.Serial(port=device, baudrate=38400, timeout=0)
        self.ser.open()
        self.send([0xAA])
        self.receive()
        self.fw = self.getFirmwareVersion()
        print "Firware version = %s" %(self.fw)
        
        self.deviceID = ord(self.getConfigurationParameter(0))
        self.PWM = ord(self.getConfigurationParameter(1))
        
    def send(self, data):
        data_to_send = [chr(x) for x in data]
        for byte in data_to_send:
            self.ser.write(byte)

    def receive(self):
        time.sleep(.1)
        return self.ser.read()
    
    def close(self):
        self.ser.close()
        
    def __del__(self):
        self.close()

    def getFirmwareVersion(self):
        self.send([0x81])
        data =  self.receive()
        return data
    
    def getConfigurationParameter(self, param):
        self.send([0x83,param])
        data =  self.receive()
        return data

    def setConfigurationParameter(self, param, value):
        self.send([0x84,param, value, 0x55, 0x2A])
        data =  self.receive()
        return data
    
    def setMotor0Speed(self, speed=60, forw=0):
        if forw:
            command = 0x88
        else:
            command = 0x89
        if speed > 127:
            self.send([command,0x7F])
            self.send([command,speed - 127])
        else:
            self.send([command+1,speed])

    def setMotor1Speed(self, speed=60, forw=0):
        if forw:
            command = 0x8C
        else:
            command = 0x8E
        self.send([command,speed&0x7F])
        time.sleep(.1)
        self.send([command+1,speed>>1])
        
        
    def setMotorSpeed(self, motor=0, speed=60, forw=0):
        if motor==0:
            self.setMotor0Speed(speed, forw)
        else:
            self.setMotor1Speed(speed, forw)
            
    def setMotorCoast(self, motor=0):
        if motor:
            command = 0x87
        else:
            command = 0x86
        self.send([command])
        
if __name__ == '__main__':
    print "Starting Motor contoller"
    mot = MOTOR('/dev/ttyAMA0')
