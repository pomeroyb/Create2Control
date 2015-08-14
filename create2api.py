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
        
class Create2(object):
    """The top level class for controlling a Create2.
        This is the only class that outside scripts should be interacting with.    
    
    """
    
    def __init__(self):
        #Nothing yet
        self.SCI = SerialCommandInterface()
    
    def start():
        #SCI.send(configData['opcodes']['start'],0)
        
    def reset():
        #SCI.send(configData['opcodes']['reset'],0)
        
    def stop():
        #SCI.send(configData['opcodes']['stop'],0)
        
    def baud():
        #SCI.send(configData['opcodes']['baud'],0)
    
    def safe():  ####THIS IS WHERE I GOT BORED
        #SCI.send(configData['opcodes']['start'],0)
    
    def full():
        #SCI.send(configData['opcodes']['start'],0)
    
    def clean():
        #SCI.send(configData['opcodes']['start'],0)
    
    def max():
        #SCI.send(configData['opcodes']['start'],0)
    
    def spot():
        #SCI.send(configData['opcodes']['start'],0)
    
    def seek_dock():
        #SCI.send(configData['opcodes']['start'],0)
    
    def power():
        #SCI.send(configData['opcodes']['start'],0)
    
    def schedule():
        #SCI.send(configData['opcodes']['start'],0)
    
    def set_day_time():
        #SCI.send(configData['opcodes']['start'],0)
    
    def drive():
        #SCI.send(configData['opcodes']['start'],0)
    
    def drive_direct():
        #SCI.send(configData['opcodes']['start'],0)
    
    def drive_pwm():
        #SCI.send(configData['opcodes']['start'],0)
    
    def motors():
        #SCI.send(configData['opcodes']['start'],0)
    
    def motors_pwm():
        #SCI.send(configData['opcodes']['start'],0)
    
    def led():
        #SCI.send(configData['opcodes']['start'],0)
    
    def scheduling_led():
        #SCI.send(configData['opcodes']['start'],0)
    
    def digit_led_raw():
        #SCI.send(configData['opcodes']['start'],0)
    
    def buttons():
        #SCI.send(configData['opcodes']['start'],0)
    
    def digit_led_ascii():
        #SCI.send(configData['opcodes']['start'],0)
    
    def song():
        #SCI.send(configData['opcodes']['start'],0)
    
    def play():
        #SCI.send(configData['opcodes']['start'],0)
    
    def sensors():
        #SCI.send(configData['opcodes']['start'],0)
    
    def query_list():
        #SCI.send(configData['opcodes']['start'],0)
    
    def stream():
        #SCI.send(configData['opcodes']['start'],0)
    
    def pause_resume_stream():
        #SCI.send(configData['opcodes']['start'],0)

        






