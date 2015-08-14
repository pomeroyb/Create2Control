import json
import serial

#first thing we want to do is load up our config file with our opcodes and other data.

configFileName = 'config.json'
configData = None
baud = 115200

with open(configFileName, 'r') as fileData:
    try:
        json.load(fileData, configData)
        print 'Loaded config and opcodes'
    except ValueError, e:
        print 'shits fucked up yo. No config and data'
        
class SerialCommandInterface(object):
    """This class handles sending commands to the Create2.
    
    """
    
    def __init__(self):
        self.ser = serial.Serial(0)
        self.ser.baudrate = baud
        print self.ser.name
        if self.ser.isOpen(): 
            #print "port was open"
            self.ser.close()
        self.ser.open()
    
    def send(self, opcode, data):
        sendRaw(data)
    
    def sendRaw(self, data):
        #This converts your nice human readable data into the necesary serial data.
        self.ser.write()
        
class SendCommand(object):
    """A wrapper class that holds all possible opcodes you can send
    """
    
    def __init__(self):
        #Nothing yet
    
    def start():
        #send(configData['opcodes']['start'],0)
        
    def reset():
        #send(configData['opcodes']['reset'],0)
        
    def stop():
        #send(configData['opcodes']['stop'],0)
        
    def baud():
        #send(configData['opcodes']['baud'],0)
    
    def safe():  ####THIS IS WHERE I GOT BORED
        #send(configData['opcodes']['start'],0)
    
    def full():
        #send(configData['opcodes']['start'],0)
    
    def clean():
        #send(configData['opcodes']['start'],0)
    
    def max():
        #send(configData['opcodes']['start'],0)
    
    def spot():
        #send(configData['opcodes']['start'],0)
    
    def seek_dock():
        #send(configData['opcodes']['start'],0)
    
    def power():
        #send(configData['opcodes']['start'],0)
    
    def schedule():
        #send(configData['opcodes']['start'],0)
    
    def set_day_time():
        #send(configData['opcodes']['start'],0)
    
    def drive():
        #send(configData['opcodes']['start'],0)
    
    def drive_direct():
        #send(configData['opcodes']['start'],0)
    
    def drive_pwm():
        #send(configData['opcodes']['start'],0)
    
    def motors():
        #send(configData['opcodes']['start'],0)
    
    def motors_pwm():
        #send(configData['opcodes']['start'],0)
    
    def led():
        #send(configData['opcodes']['start'],0)
    
    def scheduling_led():
        #send(configData['opcodes']['start'],0)
    
    def digit_led_raw():
        #send(configData['opcodes']['start'],0)
    
    def buttons():
        #send(configData['opcodes']['start'],0)
    
    def digit_led_ascii():
        #send(configData['opcodes']['start'],0)
    
    def song():
        #send(configData['opcodes']['start'],0)
    
    def play():
        #send(configData['opcodes']['start'],0)
    
    def sensors():
        #send(configData['opcodes']['start'],0)
    
    def query_list():
        #send(configData['opcodes']['start'],0)
    
    def stream():
        #send(configData['opcodes']['start'],0)
    
    def pause_resume_stream():
        #send(configData['opcodes']['start'],0)
    