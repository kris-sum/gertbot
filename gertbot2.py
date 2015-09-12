#
# This code requires python2
# Todo : detect and bom-out if using python3
#

import termios, os, time, sys
PRE            = 0xA0
POST           = 0x50

CMD_OPMODE     = 0x01 # <ID> <mode>
CMD_STOPSHORT  = 0x02 # <ID> <stopmask> 
CMD_BRD_STATUS = 0x03 # <ID> 
CMD_LINFREQ    = 0x04 # <ID> <MS><LS> 
CMD_LINDC      = 0x05 # <ID> <MS><LS>
CMD_LINON      = 0x06 # <ID> <dir>
CMD_GET_ERROR  = 0x07 # <ID> 
CMD_STEP       = 0x08 # <ID> <MS><MM><LS>
CMD_STEPFREQ   = 0x09 # <ID> <MS><MM><LS>
CMD_STOPALL    = 0x0A # 0x81
CMD_STOP2ND    = 0x81 #
CMD_OD         = 0x0B # <ID> <on/off>
CMD_DAC        = 0x0C # <ID> <MS><LS>
CMD_GET_ADC    = 0x0D # <ID> <MS><LS>
CMD_READIO     = 0x0E # <ID> <MS><MM><LS>
CMD_WRITEIO    = 0x0F # <ID> <MS><MM><LS>
CMD_SETIO      = 0x10 # <ID> <MS><MM><LS>
CMD_SETADCDAC  = 0x11 # <ID> <ADC><DAC>
CMD_CONFIGURE  = 0x12 # <ID> <MS><LS>
CMD_VERSION    = 0x13 # <ID>
CMD_MOT_STATUS = 0x14 # <ID>
CMD_SYNC       = 0x15 # 0x18
CMD_POLL       = 0x16 # <ID>
CMD_PWR_OFF    = 0x17 # 0x81
CMD_IO_STATUS  = 0x18 # <ID>
CMD_DCC_MESS   = 0x19 # <ID> <format> <d0> <d1> <d2> <d3> <d4>
CMD_DCC_CONFIG = 0x1A # <ID> <repeat> <preamble> <dc_ms> <dc_ls>
CMD_MOT_CONFIG = 0x1B # <ID> 
CMD_MOT_MISSED = 0x1C # <ID>
CMD_SET_RAMP   = 0x1D # <ID> <up|down> <hlt>
CMD_ENDSTOP    = 0x1F # <ID> <type> <timeA> <timeB>
CMD_SHORTHOT   = 0x21 # <ID> <short> 
CMD_SETBAUD    = 0x22 # 18 81 <baud>
CMD_QUAD       = 0x23 # Quadrature encoder on 
CMD_QUAD_READ  = 0x24 # Get value
CMD_QUAD_GOTO  = 0x25 # Goto position
CMD_QUAD_LIMIT = 0x26 # Set limits 

###################

MODE_OFF        = 0x00
MODE_BRUSH      = 0x01
MODE_DCC        = 0x02
MODE_STEPG_OFF  = 0x08
MODE_STEPP_OFF  = 0x09
MODE_STEPG_PWR  = 0x18
MODE_STEPP_PWR  = 0x19
MODE_STEP_MASK  = 0x0C

ENDSTOP_OFF  =  0
ENDSTOP_LOW  =  1
ENDSTOP_HIGH =  2

MOVE_STOP = 0   
MOVE_A    = 1
MOVE_B    = 2

RAMP_OFF=  0 # -
RAMP_010=  1 # 0.10 sec. 
RAMP_025=  2 # 0.25 sec.
RAMP_050=  3 # 0.50 sec.
RAMP_075=  4 # 0.75 sec.
RAMP_100=  5 # 1.00 sec.
RAMP_125=  6 # 1.25 sec.
RAMP_150=  7 # 1.50 sec.
RAMP_175=  8 # 1.75 sec.
RAMP_200=  9 # 2.00 sec.
RAMP_225= 10 # 2.25 sec.
RAMP_250= 11 # 2.50 sec.
RAMP_300= 12 # 3.00 sec.
RAMP_400= 13 # 4.00 sec.
RAMP_500= 14 # 5.00 sec.
RAMP_700= 15 # 7.00 sec.

SHORT_NONE  = 0 # Stop nothing but reduce current
SHORT_CHAN  = 1 # Stop channel
SHORT_DUAL  = 2 # Stop channel pair
SHORT_BOARD = 3 # Stop board
SHORT_SYST  = 4 # Stop system

QUAD_EMPTY   = 0x00 # No flags
QUAD_REVERSE = 0x01 # Reverse counting
QUAD_GOSLOW  = 0x02 # GOTO & limits have slow
QUAD_TOP     = 0x04 # Have top limit
QUAD_BOT     = 0x08 # Have bottom limit
QUAD_ON      = 0x10 # ON/OFF only used in command



STOP_OFF  =  0
STOP_ON   =  1

PIN_SAME    = 0
PIN_INPUT   = 1
PIN_OUTPUT  = 2
PIN_ENDSTOP = 3
PIN_ADC     = 4
PIN_DAC     = 5
PIN_I2C     = 6

DAC_MIN = 0.7
DAC_MAX = 2.7 

filehandle = -1

def open_uart(port):
   global filehandle
   filehandle=os.open("/dev/ttyAMA0",os.O_RDWR|os.O_NOCTTY|os.O_NDELAY|os.O_NONBLOCK)
   port_attr = termios.tcgetattr(filehandle)
   # [ iflag, oflag, cflag, lflag, ispeed, ospeed]
   #   [0]    [1]     [2]    [3]     [4]     [5]
   port_attr[0] = termios.IGNBRK
   # port_attr.c_iflag &= ~(termios.IXON|termios.IXOFF|termios.IXANY)
   port_attr[1] = 0
   port_attr[2] = port_attr[2] | termios.CLOCAL | \
                  termios.CREAD # ignore mode status, enable rec.
   port_attr[2] = port_attr[2] & ~(termios.PARENB | \
                  termios.PARODD | termios.CSTOPB) # No parity, 1 stop bit
   port_attr[3] = 0
   port_attr[4] = termios.B57600
   port_attr[5] = termios.B57600
   termios.tcsetattr(filehandle,termios.TCSANOW,port_attr)

def get_version(board) :
   dest = (board<<2)
   wrtbuf = [0xA0, CMD_VERSION, dest, POST, POST, POST, POST]
   os.write(filehandle,bytearray(wrtbuf))
   termios.tcdrain(filehandle)
   ok , data = read_uart(4)
   if (not ok) : # or wrtbuf[0]!=CMD_GET_ERROR or wrtbuf[1]!=dest) :
     return 0
   # convert xx.yy into xx*100+yy 
   # thus version 2.5 comes out as 205
   val = data[2]*100 + data[3]
   return val

def read_uart(num_bytes) :
  if num_bytes>16 : raise
  retry = 4
  # buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 ]
  while (retry) :
    read_fail = 0
    try:
        datastring = os.read(filehandle, num_bytes)
        # datastring += "\0"*(16 - len(datastring))
        # convert to bytearray
        buffer = bytearray()
        buffer.extend(datastring)
    except OSError as err:
        if err.errno == os.errno.EAGAIN or err.errno == os.errno.EWOULDBLOCK:
            read_fail = 1
            pass
        else:
            raise  # something else has happened -- better reraise
    
    if read_fail==1: 
        # try again 
        retry = retry - 1
    else:
        # buffer contains some received data 
        if len(buffer)==num_bytes :
          return True, buffer
  return False, buffer

def activate_opendrain(board,drain0,drain1) :
   # GB_CHECK(board>=0 && board<=3,  "activate_opendrain illegal board\n")
   mask = 0
   if drain0!=0 :
      mask = mask | 0x01
   if drain1!=0 :
      mask = mask | 0x02
   wrtbuf = [PRE, CMD_OD, board<<2, mask ,POST]
   os.write(filehandle,bytearray(wrtbuf))  
