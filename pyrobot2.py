#!/usr/bin/python

# The MIT License
#
# Copyright (c) 2007 Damon Kohler
# Copyright (c) 2015 Jonathan Le Roux (Modifications for Create 2)
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

from __future__ import with_statement

"""iRobot Roomba Serial Control Interface (SCI) and Create Open Interface (OI).
PyRobot was originally based on openinterface.py, developed by iRobot
Corporation. Many of the docstrings from openinterface.py, particularly those
which describe the specification, are also used here. Also, docstrings may
contain specification text copied directly from the Roomba SCI Spec Manual and
the Create Open Interface specification.

Since SCI is a subset of OI, PyRobot first defines the Roomba's functionality
in the Roomba class and then extends that with the Create's additional
functionality in the Create class. In addition, since OI is built on SCI the
SerialCommandInterface class is also used for OI.
"""
__author__ = "damonkohler@gmail.com (Damon Kohler), leroux@merl.com (Jonathan Le Roux)"

import logging
import math
import serial
import struct
import time
import threading
import traceback

ROOMBA_OPCODES = dict(
    start = 128,
    baud = 129,
    control = 130,
    safe = 131,
    full = 132,
    power = 133,
    spot = 134,
    clean = 135,
    max = 136,
    drive = 137,
    motors = 138,
    leds = 139,
    song = 140,
    play = 141,
    sensors = 142,
    force_seeking_dock = 143,
    )

CREATE_OPCODES = dict(
    soft_reset = 7,
    low_side_drivers = 138,
    pwm_low_side_drivers = 144,
    direct_drive = 145,
    digital_outputs = 147,
    stream = 148,
    query_list = 149,
    pause_resume_stream = 150,
    send_ir = 151,
    script = 152,
    play_script = 153,
    show_script = 154,
    wait_time = 155,
    wait_distance = 156,
    wait_angle = 157,
    wait_event = 158,
    )

CREATE2_OPCODES = dict(
    soft_reset = 7,
    query = 142,
    pwm_motors = 144,
    drive_wheels = 145,
    drive_pwm = 146,
    stream = 148,
    query_list = 149,
    do_stream = 150,
    scheduling_leds = 162,
    digit_leds_raw = 163,
    digit_leds_ascii = 164,
    buttons = 165,
    schedule = 166,
    set_day_time = 167,
    stop = 173,
    )

REMOTE_OPCODES = {
    # Remote control.
    0: 'none',
    129: 'left',
    130: 'forward',
    131: 'right',
    132: 'spot',
    133: 'max',
    134: 'small',
    135: 'medium',
    136: 'large',
    136: 'clean',
    137: 'pause',
    138: 'power',
    139: 'arc-left',
    140: 'arc-right',
    141: 'drive-stop',
    # Scheduling remote.
    142: 'send-all',
    143: 'seek-dock',
    # Home base.
    240: 'reserved',
    242: 'force-field',
    244: 'green-buoy',
    246: 'green-buoy-and-force-field',
    248: 'red-buoy',
    250: 'red-buoy-and-force-field',
    252: 'red-buoy-and-green-buoy',
    254: 'red-buoy-and-green-buoy-and-force-field',
    255: 'none',
    # Roomba 600 drive-on charger.
    160: 'reserved',
    161: 'force-field',
    164: 'green-buoy',
    165: 'green-buoy-and-force-field',
    168: 'red-buoy',
    169: 'red-buoy-and-force-field',
    172: 'red-buoy-and-green-buoy',
    173: 'red-buoy-and-green-buoy-and-force-field',
    # Roomba 600 Virtual Wall.
    162: 'virtual-wall'
    }

BAUD_RATES = (  # In bits per second.
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    14400,
    19200,
    28800,
    38400,
    57600,  # Default for Roomba and Create
    115200) # Default for Create 2

CHARGING_STATES = (
    'not-charging',
    'charging-recovery',
    'charging',
    'trickle-charging',
    'waiting',
    'charging-error')

OI_MODES = (
    'off',
    'passive',
    'safe',
    'full')

#SENSOR_GROUP_PACKET_LENGTHS = (26, 10, 6, 10, 14, 12, 52, 80, 28, 12, 9)
SENSOR_GROUP_PACKET_LENGTHS = {
    0: 26,
    1: 10,
    2: 6,
    3: 10,
    4: 14,
    5: 12,
    6: 52,
    100: 80,
    101: 28,
    102: 12,
    103: 9 }

# From: http://www.harmony-central.com/MIDI/Doc/table2.html
MIDI_TABLE = {'rest': 0, 'R': 0, 'pause': 0,
              'G1': 31, 'G#1': 32, 'A1': 33,
              'A#1': 34, 'B1': 35,

              'C2': 36, 'C#2': 37, 'D2': 38,
              'D#2': 39, 'E2': 40, 'F2': 41,
              'F#2': 42, 'G2': 43, 'G#2': 44,
              'A2': 45, 'A#2': 46, 'B2': 47,

              'C3': 48, 'C#3': 49, 'D3': 50,
              'D#3': 51, 'E3': 52, 'F3': 53,
              'F#3': 54, 'G3': 55, 'G#3': 56,
              'A3': 57, 'A#3': 58, 'B3': 59,

              'C4': 60, 'C#4': 61, 'D4': 62,
              'D#4': 63, 'E4': 64, 'F4': 65,
              'F#4': 66, 'G4': 67, 'G#4': 68,
              'A4': 69, 'A#4': 70, 'B4': 71,

              'C5': 72, 'C#5': 73, 'D5': 74,
              'D#5': 75, 'E5': 76, 'F5': 77,
              'F#5': 78, 'G5': 79, 'G#5': 80,
              'A5': 81, 'A#5': 82, 'B5': 83,

              'C6': 84, 'C#6': 85, 'D6': 86,
              'D#6': 87, 'E6': 88, 'F6': 89,
              'F#6': 90, 'G6': 91, 'G#6': 92,
              'A6': 93, 'A#6': 94, 'B6': 95,

              'C7': 96, 'C#7': 97, 'D7': 98,
              'D#7': 99, 'E7': 100, 'F7': 101,
              'F#7': 102, 'G7': 103, 'G#7': 104,
              'A7': 105, 'A#7': 106, 'B7': 107,

              'C8': 108, 'C#8': 109, 'D8': 110,
              'D#8': 111, 'E8': 112, 'F8': 113,
              'F#8': 114, 'G8': 115, 'G#8': 116,
              'A8': 117, 'A#8': 118, 'B8': 119,

              'C9': 120, 'C#9': 121, 'D9': 122,
              'D#9': 123, 'E9': 124, 'F9': 125,
              'F#9': 126, 'G9': 127}
              
# Because a 7 segment display is not sufficient to display alphabetic
# characters properly, all characters are an approximation, and not all
# ASCII codes are implemented.
ASCII_TABLE = {' ': 32, '!': 33,
              '"': 34, '#': 35,
              '%': 37, '&': 38,
              '\'': 39, '[': 40,
              ']': 41, ',':  44,
              '-': 45, '.': 46, '/': 47,
              '0': 48, '1': 49, '2': 50,
              '3': 51, '4': 52, '5': 53,
              '6': 54, '7': 55, '8': 56,
              '9': 57, ':': 58, ';': 59,
              '<': 60, '=': 61, '>': 62,
              '?': 63, 'A': 65,
              'B': 66, 'C': 67, 'D': 68,
              'E': 69, 'F': 70, 'G': 71,
              'H': 72, 'I': 73, 'J': 74,
              'K': 75, 'L': 76, 'M': 77,
              'N': 78, 'O': 79, 'P': 80,
              'Q': 81, 'R': 82, 'S': 83,
              'T': 84, 'U': 85, 'V': 86,
              'W': 87, 'X': 88, 'Y': 89,
              'Z': 90, '\\': 92,
              '^': 94, '_': 95, '`': 96,
              '{': 123, '|': 124,
              '}': 125, '~': 126}

# Drive constants.
RADIUS_TURN_IN_PLACE_CW = -1
RADIUS_TURN_IN_PLACE_CCW = 1
RADIUS_STRAIGHT = 32768
RADIUS_MAX = 2000

VELOCITY_MAX = 500  # mm/s
VELOCITY_SLOW = int(VELOCITY_MAX * 0.33)
VELOCITY_FAST = int(VELOCITY_MAX * 0.66)
VELOCITY_MIN = 25  # mm/s

WHEEL_SEPARATION = 298  # mm
WHEEL_SEPARATION_CREATE2 = 235  # mm (I'm measuring ~233/234)

SERIAL_TIMEOUT = 2  # Number of seconds to wait for reads. 2 is generous.
START_DELAY = 5  # Time it takes the Roomba/Create to boot.


assert struct.calcsize('H') == 2, 'Expecting 2-byte shorts.'


class PyRobotError(Exception):
  pass


class SerialCommandInterface(object):

  """A higher-level wrapper around PySerial specifically designed for use with
  iRobot's SCI.

  """
  def __init__(self, tty, baudrate):
    self.ser = serial.Serial(tty, baudrate=baudrate, timeout=SERIAL_TIMEOUT)
    """On Windows, closing before opening seems to help"""
    if self.ser.isOpen(): 
        #print "port was open"
        self.ser.close()
    self.ser.open()
    print 'Port opened'
    self.opcodes = {}
    self.lock = threading.RLock()

  def Wake(self):
    """Wake up robot."""
    self.ser.setRTS(0)
    time.sleep(0.25)
    self.ser.setRTS(1)
    time.sleep(1)  # Technically it should wake after 500ms.

  def AddOpcodes(self, opcodes):
    """Add available opcodes to the SCI."""
    self.opcodes.update(opcodes)

  def Send(self, bytes):
    """Send a string of bytes to the robot."""
    with self.lock:
      self.ser.write(struct.pack('B' * len(bytes), *bytes))

  def Read(self, num_bytes):
    """Read a string of 'num_bytes' bytes from the robot."""
    logging.debug('Attempting to read %d bytes from SCI port.' % num_bytes)
    with self.lock:
      data = self.ser.read(num_bytes)
    logging.debug('Read %d bytes from SCI port.' % len(data))
    if not data:
      raise PyRobotError('Error reading from SCI port. No data.')
    if len(data) != num_bytes:
      raise PyRobotError('Error reading from SCI port. Wrong data length.')
    return data

  def FlushInput(self):
    """Flush input buffer, discarding all its contents."""
    logging.debug('Flushing serial input buffer.')
    self.ser.flushInput()

  def __getattr__(self, name):
    """Creates methods for opcodes on the fly.

    Each opcode method sends the opcode optionally followed by a string of
    bytes.

    """
    if name in self.opcodes:
      def SendOpcode(*bytes):
        logging.debug('Sending opcode %s.' % name)
        self.Send([self.opcodes[name]] + list(bytes))
      return SendOpcode
    raise AttributeError


class RoombaSensors(object):

  """Retrive and decode the Roomba's sensor data.

  Some of the specification is included in the docstrings. For a complete
  description, see the Roomba SCI Sepc Manual.

  """
  def __init__(self, robot):
    self.robot = robot
    self.data = {}  # Last sensor readings.

  def Clear(self):
    """Clear out old sensor data."""
    self.data = {}

  def __getitem__(self, name):
    """Indexes into sensor data."""
    return self.data[name]

  def __contains__(self, name):
    """Indexes into sensor data."""
    return name in self.data

  def _MakeHumanReadable(self, sensor, mapping):
    """Change a sensor value to it's human readable form."""
    try:
      
      self.data[sensor] = mapping[self.data[sensor]]
    except (KeyError, IndexError):
      logging.debug(traceback.format_exc())
      raise PyRobotError('Invalid sensor data.')

  def _DecodeGroupPacket0(self, bytes):
    """Decode sensord data from a request for group 0 (all data)."""
    # NOTE(damonkohler): We decode sensor data in reverse order for better pop
    # performance.
    self.DecodeUnsignedShort('capacity', bytes.pop(), bytes.pop())  # mAh
    self.DecodeUnsignedShort('charge', bytes.pop(), bytes.pop())  # mAh
    self.DecodeByte('temperature', bytes.pop())  # C
    self.DecodeShort('current', bytes.pop(), bytes.pop())  # mA
    self.DecodeUnsignedShort('voltage', bytes.pop(), bytes.pop())  # mV
    self.DecodeUnsignedByte('charging-state', bytes.pop())
    self._MakeHumanReadable('charging-state', CHARGING_STATES)
    self.Angle(bytes.pop(), bytes.pop(), 'degrees')
    self.DecodeShort('distance', bytes.pop(), bytes.pop())  # mm
    self.Buttons(bytes.pop())
    self.DecodeUnsignedByte('remote-opcode', bytes.pop())
    self._MakeHumanReadable('remote-opcode', REMOTE_OPCODES)
    self.DecodeUnsignedByte('dirt-detector-right', bytes.pop())
    self.DecodeUnsignedByte('dirt-detector-left', bytes.pop())
    self.MotorOvercurrents(bytes.pop())
    self.DecodeBool('virtual-wall', bytes.pop())
    self.DecodeBool('cliff-right', bytes.pop())
    self.DecodeBool('cliff-front-right', bytes.pop())
    self.DecodeBool('cliff-front-left', bytes.pop())
    self.DecodeBool('cliff-left', bytes.pop())
    self.DecodeBool('wall', bytes.pop())
    self.BumpsWheeldrops(bytes.pop())

  def RequestPacket(self, packet_id):
    """Request a sensor packet."""
    with self.robot.sci.lock:
      logging.debug('Requesting sensor packet %d.' % packet_id)
      self.robot.sci.FlushInput()
      self.robot.sci.sensors(packet_id)
      length = SENSOR_GROUP_PACKET_LENGTHS[packet_id]
      data = list(self.robot.sci.Read(length))
      return data

  def GetAll(self):
    """Request and decode all available sensor data."""
    bytes = self.RequestPacket(0)
    if bytes is not None:
      self._DecodeGroupPacket0(bytes)

  def Angle(self, low, high, unit=None):
    """The angle that Roomba has turned through since the angle was last
    requested. The angle is expressed as the difference in the distance
    traveled by Roomba's two wheels in millimeters, specifically the right
    wheel distance minus the left wheel distance, divided by two. This makes
    counter-clockwise angles positive and clockwise angles negative. This can
    be used to directly calculate the angle that Roomba has turned through
    since the last request. Since the distance between Roomba's wheels is
    258mm, the equations for calculating the angles in familiar units are:

    Angle in radians = (2 * difference) / 258
    Angle in degrees = (360 * difference) / (258 * Pi).

    If the value is not polled frequently enough, it will be capped at its
    minimum or maximum.

    Note: Reported angle and distance may not be accurate. Roomba measures
    these by detecting its wheel revolutions. If for example, the wheels slip
    on the floor, the reported angle of distance will be greater than the
    actual angle or distance.

    """
    if unit not in (None, 'radians', 'degrees'):
      raise PyRobotError('Invalid angle unit specified.')
    self.DecodeShort('angle', low, high)
    if unit == 'radians':
      self.data['angle'] = (2 * self.data['angle']) / 258
    if unit == 'degrees':
      self.data['angle'] /= math.pi

  def BumpsWheeldrops(self, byte):
    """The state of the bump (0 = no bump, 1 = bump) and wheeldrop sensors
    (0 = wheel up, 1 = wheel dropped) are sent as individual bits.

    Note: Some robots do not report the three wheel drops separately. Instead,
    if any of the three wheels drops, all three wheel-drop bits will be set.
    You can tell which kind of robot you have by examining the serial number
    inside the battery compartment. Wheel drops are separate only if there
    is an 'E' in the serial number.

    """
    byte = struct.unpack('B', byte)[0]
    self.data.update({
        'wheel-drop-caster': bool(byte & 0x10),
        'wheel-drop-left': bool(byte & 0x08),
        'wheel-drop-right': bool(byte & 0x04),
        'bump-left': bool(byte & 0x02),
        'bump-right': bool(byte & 0x01)})

  def MotorOvercurrents(self, byte):
    """The state of the five motors overcurrent sensors are sent as individual
    bits (0 = no overcurrent, 1 = overcurrent).

    """
    byte = struct.unpack('B', byte)[0]
    self.data.update({
        'drive-left': bool(byte & 0x10),
        'drive-right': bool(byte & 0x08),
        'main-brush': bool(byte & 0x04),
        'vacuum': bool(byte & 0x02),
        'side-brush': bool(byte & 0x01)})

  def Buttons(self, byte):
    """The state of the four Roomba buttons are sent as individual bits
    (0 = button not pressed, 1 = button pressed).

    """
    byte = struct.unpack('B', byte)[0]
    self.data.update({
        'power': bool(byte & 0x08),
        'spot': bool(byte & 0x04),
        'clean': bool(byte & 0x02),
        'max': bool(byte & 0x01)})

  def DecodeBool(self, name, byte):
    """Decode 'byte' as a bool and map it to 'name'."""
    self.data[name] = bool(struct.unpack('B', byte)[0])

  # NOTE(damonkohler): We specify the low byte first to make it easier when
  # popping bytes off a list.
  def DecodeUnsignedShort(self, name, low, high):
    """Map an unsigned short from a 'high' and 'low' bytes to 'name'."""
    self.data[name] = struct.unpack('>H', high + low)[0]

  def DecodeShort(self, name, low, high):
    """Map a short from a 'high' and 'low' bytes to 'name'."""
    self.data[name] = struct.unpack('>h', high + low)[0]

  def DecodeByte(self, name, byte):
    """Map signed 'byte' to 'name'."""
    self.data[name] = struct.unpack('b', byte)[0]

  def DecodeUnsignedByte(self, name, byte):
    """Map unsigned 'byte' to 'name'."""
    self.data[name] = struct.unpack('B', byte)[0]


class Roomba(object):

  """Represents a Roomba robot."""

  def __init__(self, tty='/dev/ttyUSB0', default_baud_rate = 57600):
    self.tty = tty
    self.sci = SerialCommandInterface(tty, default_baud_rate)
    self.sci.AddOpcodes(ROOMBA_OPCODES)
    self.sensors = RoombaSensors(self)
    self.safe = True

  def ChangeBaudRate(self, baud_rate):
    """Sets the baud rate in bits per second (bps) at which SCI commands and
    data are sent according to the baud code sent in the data byte.

    The default baud rate at power up is 57600 bps for the Roomba and Create
    1, 115200 for Create 2. (See Serial Port Settings, above.) Once the baud
    rate is changed, it will persist until Roomba is power cycled by 
    removing the battery (or until the battery voltage falls below the 
    minimum required for processor operation). You must wait 100ms
    after sending this command before sending additional commands at the new
    baud rate. The SCI must be in passive, safe, or full mode to accept this
    command. This command puts the SCI in passive mode.

    """
    if baud_rate not in BAUD_RATES:
      raise PyRobotError('Invalid baud rate specified.')
    self.sci.baud(baud_rate)
    self.sci = SerialCommandInterface(self.tty, baud_rate)

  def Passive(self):
    """Put the robot in passive mode."""
    self.sci.start()
    time.sleep(0.5)

  def Control(self):
    """Start the robot's SCI interface and place it in safe mode."""
    self.Passive()
    self.sci.control()  # Also puts the Roomba in to safe mode.
    if not self.safe:
      self.sci.full()
    time.sleep(0.5)

  def Drive(self, velocity, radius):
    """Controls Roomba's drive wheels.

    NOTE(damonkohler): The following specification applies to both the Roomba
    and the Create.

    The Roomba takes four data bytes, interpreted as two 16-bit signed values
    using two's complement. The first two bytes specify the average velocity
    of the drive wheels in millimeters per second (mm/s), with the high byte
    being sent first. The next two bytes specify the radius in millimeters at
    which Roomba will turn. The longer radii make Roomba drive straighter,
    while the shorter radii make Roomba turn more. The radius is measured from
    the center of the turning circle to the center of Roomba.

    A Drive command with a positive velocity and a positive radius makes
    Roomba drive forward while turning toward the left. A negative radius
    makes Roomba turn toward the right. Special cases for the radius make
    Roomba turn in place or drive straight, as specified below. A negative
    velocity makes Roomba drive backward.

    Also see DriveStraight and TurnInPlace convenience methods.

    """
    # Mask integers to 2 bytes.
    velocity = int(velocity) & 0xffff
    radius = int(radius) & 0xffff
    # Pack as shorts to get 2 x 2 byte integers. Unpack as 4 bytes to send.
    # TODO(damonkohler): The 4 unpacked bytes will just be repacked later,
    # that seems dumb to me.
    bytes = struct.unpack('4B', struct.pack('>2H', velocity, radius))
    self.sci.drive(*bytes)

  def Stop(self):
    """Set velocity and radius to 0 to stop movement."""
    self.Drive(0, 0)

  def SlowStop(self, velocity):
    """Slowly reduce the velocity to 0 to stop movement."""
    velocities = xrange(velocity, VELOCITY_SLOW, -25)
    if velocity < 0:
      velocities = xrange(velocity, -VELOCITY_SLOW, 25)
    for v in velocities:
      self.Drive(v, RADIUS_STRAIGHT)
      time.sleep(0.05)
    self.Stop()

  def DriveStraight(self, velocity):
    """Drive in a straight line."""
    self.Drive(velocity, RADIUS_STRAIGHT)

  def TurnInPlace(self, velocity, direction):
    """Turn in place either clockwise or counter-clockwise."""
    valid_directions = {'cw': RADIUS_TURN_IN_PLACE_CW,
                        'ccw': RADIUS_TURN_IN_PLACE_CCW}
    self.Drive(velocity, valid_directions[direction])

  def Dock(self):
    """Start looking for the dock and then dock."""
    # NOTE(damonkohler): We should be able to call dock from any mode, however
    # it only seems to work from passive.
    self.sci.start()
    time.sleep(0.5)
    self.sci.force_seeking_dock()
    
  def Play(self,notes,song_id=3):
    """Play a sequence of notes of the form 'MIDI_note, note_length' """  
    notes[::2] = [MIDI_TABLE[note] for note in notes[::2]]
    self.sci.Send([self.sci.opcodes['song'], song_id, 
                   len(notes)/2] + notes + [  self.sci.opcodes['play'],song_id])


class CreateSensors(RoombaSensors):

  """Handles retrieving and decoding the Create's sensor data."""
  def __init__(self):
    super(CreateSensors, self).__init__()

  def _DecodeGroupPacket6(self, bytes):
    """Decode sensor group packet 6."""
    self.DecodeShort('left-velocity', bytes.pop(), bytes.pop())  # mm/s
    self.DecodeShort('right-velocity', bytes.pop(), bytes.pop())  # mm/s
    self.DecodeShort('radius', bytes.pop(), bytes.pop())  # mm
    self.DecodeShort('velocity', bytes.pop(), bytes.pop())  # mm/s
    self.DecodeUnsignedByte('number-of-stream-packets', bytes.pop())
    self.DecodeBool('song-playing', bytes.pop())
    self.DecodeUnsignedByte('song-number', bytes.pop())
    self.DecodeUnsignedByte('oi-mode', bytes.pop())
    self._MakeHumanReadable('oi-mode', OI_MODES)
    self.DecodeUnsignedByte('charging-sources-available', bytes.pop())
    self.DecodeUnsignedShort('user-analog-input', bytes.pop(), bytes.pop())
    self.DecodeUnsignedByte('user-digital-inputs', bytes.pop())
    self.DecodeUnsignedShort('cliff-right-signal', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort(
        'cliff-front-right-signal', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort(
        'cliff-front-left-signal', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('cliff-left-signal', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('wall-signal', bytes.pop(), bytes.pop())
    self._DecodeGroupPacket0(bytes)

  def GetAll(self):
    """Request and decode all available sensor data."""
    bytes = self.RequestPacket(6)
    if bytes is not None:
      self._DecodeGroupPacket6(bytes)


class Create(Roomba):

  """Represents a Create robot."""

  def __init__(self, tty='/dev/ttyUSB0', default_baud_rate=57600):
    super(Create, self).__init__(tty, default_baud_rate)
    self.sci.AddOpcodes(CREATE_OPCODES)
    self.sensors = CreateSensors(self)

  def Control(self):
    """Start the robot's SCI interface and place it in safe or full mode."""
    logging.info('Sending control opcodes.')
    self.Passive()
    if self.safe:
      self.sci.safe()
    else:
      self.sci.full()
    time.sleep(0.5)

  def PowerLowSideDrivers(self, drivers):
    """Enable or disable power to low side drivers.

    'drivers' should be a list of booleans indicating which low side drivers
    should be powered.

    """
    assert len(drivers) == 3, 'Expecting 3 low side driver power settings.'
    byte = 0
    for driver, power in enumerate(drivers):
      byte += (2 ** driver) * int(power)
    self.sci.low_side_drivers(byte)

  def SoftReset(self):
    """Do a soft reset of the Create."""
    logging.info('Sending soft reset.')
    self.sci.soft_reset()
    time.sleep(START_DELAY)
    self.Passive()

class Create2Sensors(CreateSensors):

  """Handles retrieving and decoding the Create 2's sensor data."""
  def __init__(self):
    super(Create2Sensors, self).__init__()
    
    
  def _DecodeGroupPacket100(self, bytes):
    """Decode sensor group packet 100."""
    self.DecodeUnsignedByte('stasis', bytes.pop())
    self.DecodeShort('side-brush-current', bytes.pop(), bytes.pop())  # mA
    self.DecodeShort('main-brush-current', bytes.pop(), bytes.pop())  # mA
    self.DecodeShort('right-motor-current', bytes.pop(), bytes.pop())  # mA
    self.DecodeShort('left-motor-current', bytes.pop(), bytes.pop())  # mA
    self.DecodeUnsignedByte('ir-opcode-right', bytes.pop())
    self._MakeHumanReadable('ir-opcode-right', REMOTE_OPCODES)
    self.DecodeUnsignedByte('ir-opcode-left', bytes.pop())
    self._MakeHumanReadable('ir-opcode-left', REMOTE_OPCODES)
    self.DecodeUnsignedShort('light-bump-right', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('light-bump-front-right', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('light-bump-center-right', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('light-bump-center-left', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('light-bump-front-left', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('light-bump-left', bytes.pop(), bytes.pop())
    self.LightBumper(bytes.pop())
    self.DecodeUnsignedShort('encoder-counts-right', bytes.pop(), bytes.pop())
    self.DecodeUnsignedShort('encoder-counts-left', bytes.pop(), bytes.pop())
    self._DecodeGroupPacket6(bytes)

  def GetAll(self):
    """Request and decode all available sensor data."""
    bytes = self.RequestPacket(100)
    if bytes is not None:
      self._DecodeGroupPacket100(bytes)

  def LightBumper(self, byte):
    """The state of the six light bumper detections are sent as individual
    bits (0 = no detection, 1 = detection).
    """
    byte = struct.unpack('B', byte)[0]
    self.data.update({
        'lt-bumper-right': bool(byte & 0x20),
        'lt-bumper-front-right': bool(byte & 0x10),
        'lt-bumper-center-right': bool(byte & 0x08),
        'lt-bumper-center-left': bool(byte & 0x04),
        'lt-bumper-front-left': bool(byte & 0x02),
        'lt-bumper-left': bool(byte & 0x01)})

  def Buttons(self, byte):
    """The state of the four Roomba buttons are sent as individual bits
    (0 = button not pressed, 1 = button pressed).
    This overrides the definition in RoombaSensors
    """
    byte = struct.unpack('B', byte)[0]
    self.data.update({
        'power': bool(byte & 0x08),
        'spot': bool(byte & 0x04),
        'clean': bool(byte & 0x02),
        'max': bool(byte & 0x01)})


class Create2(Roomba):
    
  """Represents a Create 2 robot."""

  def __init__(self, tty='COM24', default_baud_rate=115200):
    super(Create2, self).__init__(tty, default_baud_rate)
    self.sci.AddOpcodes(CREATE2_OPCODES)
    self.sensors = Create2Sensors(self)

  def Control(self):
    """Start the robot's SCI interface and place it in safe or full mode."""
    logging.info('Sending control opcodes.')
    self.Passive()
    if self.safe:
      self.sci.safe()
    else:
      self.sci.full()
    time.sleep(0.5)

  def SoftReset(self):
    """Do a soft reset of the Create."""
    logging.info('Sending soft reset.')
    self.sci.soft_reset()
    time.sleep(START_DELAY)
    self.Passive()

