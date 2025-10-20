#
# ThermostatServer-Simulator.py - This is the Python code that will be used
# to simulate the Thermostat Server. It will read the data that the
# thermostat is sending to the server over the serial port and print it 
# to the screen. 
#
# This script will loop until the user interrupts the program by 
# pressing CTRL-C
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

# Load the time module so that we can utilize the sleep method to 
# inject a pause into our operation
import time

# This imports the Python serial package to handle communications over the
# Raspberry Pi's serial port. 
import serial

# Because we imported the entire package instead of just importing Serial and
# some of the other flags from the serial package, we need to reference those
# objects with dot notation.
#
# e.g. ser = serial.Serial
#
ser = serial.Serial(
        port='/dev/ttyUSB0', # This command assumes that the USB -> TTL cable
                             # is installed and the device that it uses is 
                             # /dev/ttyUSB0. This is the case with the USB -> TTL
                             # cable and Raspberry Pi 4B included in your kit.
        baudrate = 115200,   # This sets the speed of the serial interface in
                             # bits/second
        parity=serial.PARITY_NONE,      # Disable parity
        stopbits=serial.STOPBITS_ONE,   # Serial protocol will use one stop bit
        bytesize=serial.EIGHTBITS,      # We are using 8-bit bytes 
        timeout=1          # Set timeout to 1
)

# Setup loop variable
repeat = True

# Loop until the user enters a keyboard interrupt with CTRL-C
while repeat:
        try:
                # Read a line from the serial port. 
                # This also decodes the result into a utf-8 String (utf-8 is the
                # default North American English character set) and
                # normalizes the input to lower case.
                #
                # This will block until data is available
                dataline = ((ser.readline()).decode("utf-8")).lower()

                #
                # Display to the console
                #
                if(len(dataline) > 1):
                        print(dataline)

        except KeyboardInterrupt:
                # We only reach here when the user has processed a Keyboard
                # Interrupt by pressing CTRL-C, so Exit cleanly
                repeat = False