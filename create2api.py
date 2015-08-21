import json
import serial
import struct
import os


class Error(Exception):
    """Error"""
    pass


    
class ROIDataByteError(Error):
    """Exception raised for errors in ROI data bytes.
    
        Attributes:
            msg -- explanation of the error
    """
    
    def __init__(self, msg):
        self.msg = msg

class ROIFailedToSendError(Error):
    """Exception raised when an error in data bytes prevented a packet to be sent
    
        Attributes:
            msg -- explanation of the error    
    """
    def __init__(self, msg):
        self.msg = msg

class ROIFailedToReceiveError(Error):
    """Exception raised when there is an error in the data received from the Create 2
        
        Attributes:
            msg -- explanation of the error
    """
    def __init__(self,msg):
        self.msg = msg


        
class Config(object):
    """This class handles loading and saving config files that store the
        Opcodes and other useful dicts
    
    """
    
    def __init__(self):
        self.fname = 'config.json'
        self.data = None
    
    def load(self):
        """ Loads a Create2 config file, that holds various dicts of opcodes.
        
        """
        if os.path.isfile(self.fname):
            #file exists, load it
            with open(self.fname) as fileData:
                try:
                    self.data = json.load(fileData)
                    print 'Loaded config and opcodes'
                except ValueError, e:
                    print 'Could not load config'
        else:
            #couldn't find file
            print "No config file found"
            raise ValueError('could not find config')
    
    

        
class SerialCommandInterface(object):
    """This class handles sending commands to the Create2.
    
    """
    

    
    def __init__(self):
        com = 23
        baud = 115200
        
        self.ser = serial.Serial()
        self.ser.port = com
        self.ser.baudrate = baud
        print self.ser.name
        if self.ser.isOpen(): 
            print "port was open"
            self.ser.close()
        self.ser.open()
        print "opened port"
    
    def send(self, opcode, data):
        #First thing to do is convert the opcode to a tuple.
        temp_opcode = (opcode,)
        bytes = None
        
        if data == None:
            #Sometimes opcodes don't need data. Since we can't add
            # a None type to a tuple, we have to make this check.
            bytes = temp_opcode
        else:
            #Add the opcodes and data together
            bytes = temp_opcode + data
        self.ser.write(struct.pack('B' * len(bytes), *bytes))
    
    def Read(self, num_bytes):
        """Read a string of 'num_bytes' bytes from the robot.
        
            Arguments:
                num_bytes: The number of bytes we expect to read.
        """
        #logging.debug('Attempting to read %d bytes from SCI port.' % num_bytes)
        data = self.ser.read(num_bytes)
        #logging.debug('Read %d bytes from SCI port.' % len(data))
        if not data:
            raise ROIFailedToReceiveError('Error reading from SCI port. No data.')
        if len(data) != num_bytes:
            raise ROIFailedToReceiveError('Error reading from SCI port. Wrong data length.')
        return data
    
    def Close(self):
        """Closes the serial connection.
        """
        self.ser.close()
        
        
class Create2(object):
    """The top level class for controlling a Create2.
        This is the only class that outside scripts should be interacting with.    
    
    """
    
    def __init__(self):
        #Nothing yet
        self.SCI = SerialCommandInterface()
        self.config = Config()
        self.config.load()
    
    def destroy(self):
        """Closes up serial ports and terminates connection to the Create2
        """
        self.SCI.Close()
        print 'Disconnected'
    
    
    """ START OF OPEN INTERFACE COMMANDS
    """
    def start(self):
        self.SCI.send(self.config.data['opcodes']['start'], None)
        
    def reset(self):
        self.SCI.send(self.config.data['opcodes']['reset'], None)
        
    def stop(self):
        self.SCI.send(self.config.data['opcodes']['stop'], None)
        
    def baud(self, baudRate):
        baud_dict = {
            300:0,
            600:1,
            1200:2,
            2400:3,
            4800:4,
            9600:5,
            14400:6,
            19200:7,
            28800:8,
            38400:9,
            57600:10,
            115200:11
            }
        if baudRate in baud_dict:
            self.SCI.send(self.config.data['opcodes']['baud'], tuple(baud_dict[baudRate]))
        else:
            raise ROIDataByteError("Invalid buad rate")
    
    
    def safe(self):
        self.SCI.send(self.config.data['opcodes']['safe'], None)
    
    def full(self):
        self.SCI.send(self.config.data['opcodes']['full'], None)
    
    def clean(self):
        self.SCI.send(self.config.data['opcodes']['clean'], None)
    
    def max(self):
        self.SCI.send(self.config.data['opcodes']['max'], None)
    
    def spot(self):
        self.SCI.send(self.config.data['opcodes']['spot'], None)
    
    def seek_dock(self):
        self.SCI.send(self.config.data['opcodes']['seek_dock'], None)
    
    def power(self):
        self.SCI.send(self.config.data['opcodes']['power'], None)
    
    def schedule(self):
        """Not implementing this for now.
        """    
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def set_day_time(self, day, hour, minute):
        """Sets the Create2's clock
            
            Args:
                day: A string describing the day. Assumes all lowercase letters.
                hour: A number from 0-23 (24 hour format)
                minute: A number from 0-59
        """
        data = []
        noError = True
        
        day_dict = dict(
            sunday = 0,
            monday = 1,
            tuesday = 2,
            wednesday = 3,
            thursday = 4,
            friday = 5,
            saturday = 6
            )
        
        if day in day_dict:
            data[0] = day
        else:
            noError = False
            raise ROIDataByteError("Invalid day input")
        
        if hour >= 0 and hour <= 23:
            data[1] = hour
        else:
            noError = False
            raise ROIDataByteError("Invalid hour input")
        
        if minute >= 0 and minute <= 59:
            data[2] = minute
        else:
            noError = False
            raise ROIDataByteError("Invalid minute input")
            
        if noError:
            self.SCI.send(self.config.data['opcodes']['start'], tuple(data))
        else:
            raise ROIFailedToSendError("Invalid data, failed to send")
    
    def drive(self, velocity, radius): 
        """Controls the Create 2's drive wheels.
        
            Args:
                velocity: A number between -500 and 500. Units are mm/s. 
                radius: A number between -2000 and 2000. Units are mm.
                    Drive straight: 32767
                    Turn in place clockwise: -1
                    Turn in place counterclockwise: 1
        """
        noError = True
        data = []
        v = None
        r = None

        #Check to make sure we are getting sent valid velocity/radius.
        

        if velocity >= -500 and velocity <= 500:
            v = int(velocity) & 0xffff
            #Convert 16bit velocity to Hex
        else:
            noError = False
            raise ROIDataByteError("Invalid velocity input")
        
        if radius == 32767 or radius == -1 or radius == 1:
            #Special case radius
            r = int(radius) & 0xffff
            #Convert 16bit radius to Hex
        else:
            if radius >= -2000 and radius <= 2000:
                r = int(radius) & 0xffff
                #Convert 16bit radius to Hex
            else:
                noError = False
                raise ROIDataByteError("Invalid radius input")

        if noError:
            data = struct.unpack('4B', struct.pack('>2H', velocity, radius))
            #An example of what data looks like:
            #print data >> (255, 56, 1, 244)
            
            #data[0] = Velocity high byte
            #data[1] = Velocity low byte
            #data[2] = Radius high byte
            #data[3] = Radius low byte
            
            #Normally we would convert data to a tuple before sending it to SCI
            #   But struct.unpack already returns a tuple.
            self.SCI.send(self.config.data['opcodes']['drive'], data)
        else:
            raise ROIFailedToSendError("Invalid data, failed to send")
        
    
    def drive_direct(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def drive_pwm(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def motors(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def motors_pwm(self, main_pwm, side_pwm, vacuum_pwm):
        """Serial sequence: [144] [Main Brush PWM] [Side Brush PWM] [Vacuum PWM] 
            
            Arguments:
                main_pwm: Duty cycle for Main Brush. Value from -127 to 127. Positive speeds spin inward.
                side_pwm: Duty cycle for Side Brush. Value from -127 to 127. Positive speeds spin counterclockwise.
                vacuum_pwm: Duty cycle for Vacuum. Value from 0-127. No negative speeds allowed.
        """
        noError = True
        data = []
        
        #First check that our data is within bounds
        if main_pwm >= -127 and main_pwm <= 127:
            data[0] = main_pwm
        else:
            noError = False
            raise ROIDataByteError("Invalid Main Brush input")
        if side_pwm >= -127 and side_pwm <= 127:
            data[1] = side_pwm
        else:
            noError = False
            raise ROIDataByteError("Invalid Side Brush input")
        if vacuum_pwm >= 0 and vacuum_pwm <= 127:
            data[2] = vacuum_pwm
        else:
            noError = False
            raise ROIDataByteError("Invalid Vacuum input")
        
        #Send it off if there were no errors.
        if noError:
            self.SCI.send(self.config.data['opcodes']['motors_pwm'], tuple(data))
        else:
            raise ROIFailedToSendError("Invalid data, failed to send")
        
    
    def led(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def scheduling_led(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def digit_led_raw(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def buttons(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def digit_led_ascii(self, display_string):
        """This command controls the four 7 segment displays using ASCII character codes.
        
            Arguments:
                display_string: A four character string to be displayed. This must be four
                    characters. Any blank characters should be represented with a space: ' '
        """
        noError = True
        display_list = []
        if len(display_string) == 4:
            display_list = list(display_string)
        else:
            #Too many or too few characters!
            noError = False
            raise ROIDataByteError("Invalid ASCII input (Must be EXACTLY four characters)")
        if noError:
            #Need to map ascii to numbers from the dict.
            print 'map the ascii!'
            #self.SCI.send(self.config.data['opcodes']['start'], tuple(display_list))
        else:
            raise ROIFailedToSendError("Invalid data, failed to send")
        
    
    def song(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def play(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def sensors(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def query_list(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def stream(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)
    
    def pause_resume_stream(self):
        """Not implementing this for now.
        """
        #self.SCI.send(self.config.data['opcodes']['start'],0)

    """ END OF OPEN INTERFACE COMMANDS
    """
        
    def drive_straight(self, velocity):
        self.drive(velocity, 32767)





