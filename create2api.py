        # The MIT License
#
# Copyright (c) 2007 Damon Kohler
# Copyright (c) 2015 Jonathan Le Roux (Modifications for Create 2)
# Copyright (c) 2015 Brandon Pomeroy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.




import json
import serial
import struct
import os
import warnings
import time


class Error(Exception):
    """Error"""
    pass

def custom_format_warning(message, category, filename, lineno, file=None, line=None):
    return str(message) + '\n'
    #return ' %s:%s: %s:%s' % (filename, lineno, category.__name__, message)
    
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
            raise ValueError('Could not find config')
    
    

        
class SerialCommandInterface(object):
    """This class handles sending commands to the Create2.
    
    """

    def __init__(self):
        com = 23  #This should not be hard coded...
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
        print bytes
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

class sensorPacketDecoder(object):
    """ A class that handles sensor packet decoding.
    
    """
    
    def __init__(self, sensor_packet_lengths):
        self.lengths = sensor_packet_lengths
    
    def decode_packet(self, packet_id, byte_data, sensor_data):
        """ Decodes an OI packet
            
            Arguments:
                packet_id: The id of the packet. Duh.
                byte_data: The bytes that the Create 2 sent over serial
                sensor_data: A dict containg the sensor states of the Create 2
            Returns:
                A dict containing the updated sensor states of the Create 2
        """
        return_dict = None
        id = packet_id  # For shorter lines
        
        # Depending on the packet id, we will need to do different decoding.
        # Packets 1-6 and 100, 101, 106, and 107 are special cases where they
        #   contain groups of packets.
        #
        # Other packets (7-58) are single packets, but some of them have two byte
        #   data, and also need special treatment.
        
        # Hold onto your hats. This is gonna get long fast.
        if id == 0:
            print id # Size 26, contains packet 7-26
        elif id == 1:
            print id # Size 10, contais 7-16
        elif id == 2:
            print id # size 6, contains 17-20
        elif id == 3:
            print id # size 10, contains 21-26
        elif id == 4:
            print id # size 14, contains 27-34
        elif id == 5:
            print id # size 12, contains 35-42
        elif id == 6:
            print id # size 52, contains 7-42
        elif id == 7:
            print id
            #####SINGLE PACKETS BEGIN IN HERE
        elif id == 8:
            print id
        elif id == 9:
            print id
        elif id == 10:
            print id
        elif id == 11:
            print id
        elif id == 12:
            print id
        elif id == 13:
            print id
        elif id == 14:
            print id
        elif id == 15:
            print id
        elif id == 16:
            print id
        elif id == 17:
            print id
        elif id == 18:
            print id
        elif id == 19:
            print id
        elif id == 20:
            print id
        elif id == 21:
            print id
        elif id == 22:
            print id
        elif id == 23:
            print id
        elif id == 24:
            print id
        elif id == 25:
            print id
        elif id == 26:
            print id
        elif id == 27:
            print id
        elif id == 28:
            print id
        elif id == 29:
            print id
        elif id == 30:
            print id
        elif id == 31:
            print id
        elif id == 32:
            print id
        elif id == 33:
            print id
        elif id == 34:
            print id
        elif id == 35:
            print id
        elif id == 36:
            print id
        elif id == 37:
            print id
        elif id == 38:
            print id
        elif id == 39:
            print id
        elif id == 40:
            print id
        elif id == 41:
            print id
        elif id == 42:
            print id
        elif id == 43:
            print id
        elif id == 44:
            print id
        elif id == 45:
            print id
        elif id == 46:
            print id
        elif id == 47:
            print id
        elif id == 48:
            print id
        elif id == 49:
            print id
        elif id == 50:
            print id
        elif id == 51:
            print id
        elif id == 52:
            print id
        elif id == 53:
            print id
        elif id == 54:
            print id
        elif id == 55:
            print id
        elif id == 56:
            print id
        elif id == 57:
            print id
        elif id == 58:
            print id
            ##### Single Packets END
        elif id == 100:
            print id # size 80, contains 7-58 (ALL)
        elif id == 101:
            print id # size 28, contains 43-58
        elif id == 106:
            print id # size 12, contains 46-51
        elif id == 107:
            print id # size 9, contains 54-58
        else:
            print "No valid packet!"
            return_dict = sensor_data
        
        # No, Python doesn't need a switch case at all.
        
        return return_dict
        
    def decode_packet_7(self, data):
        """ Decode Packet 7 and return its value
        
            Arguments:
                data: The bytes to decode
        
            Returns: A dict of 'wheel drop and bumps'
        """
        data = struct.unpack('B', data)[0]
        return_dict = {
            'drop left': bool(byte & 0x08),
            'drop right': bool(byte & 0x04),
            'bump left': bool(byte & 0x02),
            'bump right': bool(byte & 0x01)}
        return return_dict
        
    
    def decode_bool(self, byte):
        """ Decode a byte and return the value
        
            Arguments:
                byte: The byte to be decoded
            Returns: True or False
        """
        return bool(struct.unpack('B', byte)[0])
    

    def decode_unsigned_short(self, low, high):
        """ Decode an 16 bit unsigned short from two bytes. 
        
            Arguments:
                low: The low byte of the 2's complement. This is specified first
                    to make it easier when popping bytes off a list.
                high: The high byte o the 2's complement.
            Returns: 16bit unsigned short
        """
        return struct.unpack('>H', high + low)[0]
        
    def decode_short(self, low, high):
        """ Decode an 16 bit short from two bytes. 
        
            Arguments:
                low: The low byte of the 2's complement. This is specified first
                    to make it easier when popping bytes off a list.
                high: The high byte o the 2's complement.
            Returns: 16bit short
        """
        return struct.unpack('>h', high + low)[0]
        
    def decode_byte(self, byte):
        """ Decode a signed byte into a signed char 
        
            Arguments:
                byte: The byte to be decoded
            Returns: A signed int
        """
        return struct.unpack('b', byte)[0]
    
    def decode_unsigned_byte(self, byte):
        """ Decode an unsigned byte into an unsigned char 
        
            Arguments:
                byte: The byte to be decoded
            Returns: An unsigned int
        """
        return struct.unpack('B', byte)[0]
    
    
        
        
class Create2(object):
    """The top level class for controlling a Create2.
        This is the only class that outside scripts should be interacting with.    
    
    """
    
    def __init__(self):
        
        self.SCI = SerialCommandInterface()
        self.config = Config()
        self.config.load()
        self.decoder = sensorPacketDecoder(dict(self.config.data['sensor group packet lengths']))
        self.sensor_state = dict(self.config.data['sensor data']) # Load a raw sensor dict. None of these values are correct.
        self.sleep_timer = .5
        
    
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
        """Puts the Create 2 into safe mode. Blocks for a short (<.5 sec) amount of time so the
            bot has time to change modes.
        """
        self.SCI.send(self.config.data['opcodes']['safe'], None)
        time.sleep(self.sleep_timer)
    
    def full(self):
        """Puts the Create 2 into full mode. Blocks for a short (<.5 sec) amount of time so the
            bot has time to change modes.
        """
        self.SCI.send(self.config.data['opcodes']['full'], None)
        time.sleep(self.sleep_timer)
    
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
                day: A string describing the day.
                hour: A number from 0-23 (24 hour format)
                minute: A number from 0-59
        """
        data = [None, None, None]
        noError = True
        day = day.lower()
        
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
            data[0] = day_dict[day]
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
            self.SCI.send(self.config.data['opcodes']['set_day_time'], tuple(data))
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
            data = struct.unpack('4B', struct.pack('>2H', v, r))
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
                    Due to the limited display, there is no control over upper or lowercase
                    letters. create2api will automatically convert all chars to uppercase, but
                    some letters (Such as 'B' and 'D') will still display as lowercase on the
                    Create 2's display. C'est la vie.
        """
        noError = True
        display_string = display_string.upper()
        #print display_string
        if len(display_string) == 4:
            display_list = []
        else:
            #Too many or too few characters!
            noError = False
            raise ROIDataByteError("Invalid ASCII input (Must be EXACTLY four characters)")
        if noError:
            #Need to map ascii to numbers from the dict.
            for i in range (0,4):
                #Check that the character is in the list, if it is, add it.
                if display_string[i] in self.config.data['ascii table']:
                    display_list.append(self.config.data['ascii table'][display_string[i]])
                else:
                    # Char was not available. Just print a blank space
                    # Raise an error so the software knows that the input was bad
                    display_list.append(self.config.data['ascii table'][' '])
                    warnings.formatwarning = custom_format_warning
                    warnings.warn("Warning: Char '" + display_string[i] + "' was not found in ascii table")
                
            #print display_list
            self.SCI.send(self.config.data['opcodes']['digit_led_ascii'], tuple(display_list))
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
    
    def sensors(self, packet_id):
        """Requests the OI to send a packet of sensor data bytes.
        
            Arguments:
                packet_id: Identifies which of the 58 sensor data packets should be sent back by the OI. 
        """
        # Check to make sure that the packet ID is valid.
        if packet_id in self.config.data['sensor group packet lengths']:
            # Valid packet, send request
            self.SCI.send(self.config.data['opcodes']['sensors'], tuple(packet_id))
        else:
            raise ROIFailedToSendError("Invalid packet (Must be between 0-107), failed to send")
        
    
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
        """ Will make the Create2 drive straight at the given velocity
        
            Arguments:
                velocity: Velocity of the Create2 in mm/s. Positive velocities are forward,
                    negative velocities are reverse. Max speeds are still enforced by drive()
        
        """
        self.drive(velocity, 32767)
        
    def turn_clockwise(self, velocity):
        """ Makes the Create2 turn in place clockwise at the given velocity
        
            Arguments:
                velocity: Velocity of the Create2 in mm/s. Positive velocities are forward,
                    negative velocities are reverse. Max speeds are still enforced by drive()
        """
        self.drive(velocity, -1)
        
    def turn_counter_clockwise(self, velocity):
        """ Makes the Create2 turn in place counter clockwise at the given velocity
    
            Arguments:
                velocity: Velocity of the Create2 in mm/s. Positive velocities are forward,
                    negative velocities are reverse. Max speeds are still enforced by drive()
        """
        self.drive(velocity, 1)
    
    def get_packet(self, packet_id):
        """ Requests and reads a packet from the Create 2
            
            Arguments:
                packet_id: The id of the packet you wish to collect.
            
            Returns: None if there was an error, else the decoded packet data.
        """
        
        packet_size = None
        packet_byte_data = None
        if packet_id in self.config.data['sensor group packet lengths']:
            # If a packet is in this dict, that means it is valid
            packet_size = self.config.data['sensor group packet lengths'][packet_id]
            packet_byte_data = list(self.SCI.Read(packet_size))
            # Once we have the byte data, we need to decode the packet and save the new sensor state
            self.sensor_state = self.decoder.decode_packet(packet_id, packet_byte_data, self.sensor_state)
        else:
            #The packet was invalid, raise an error
            raise ROIDataByteError("Invalid packet ID")
            return None





