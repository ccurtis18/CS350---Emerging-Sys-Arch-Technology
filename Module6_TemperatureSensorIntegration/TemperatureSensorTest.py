#
# TemperatureSensorTest.py - This is the Python code used to demonstrate
# the data that is received from the AHT20 temperature sensor board.
#
# This code works with the test circuit that was built for module 6.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

##
## Import necessary to provide timing in the main loop
##
from time import sleep

##
## Imports necessary to provide connectivity to the 
## sensor and the I2C bus
##
import board
import adafruit_ahtx0

##
## Create an I2C instance so that we can communicate with
## devices on the I2C bus.
##
i2c = board.I2C()

##
## Initialize our Temperature and Humidity sensor
##
thSensor = adafruit_ahtx0.AHTx0(i2c)

##
## Setup the flag that will control our main loop
##
repeat = True

##
## Loop until the user issues a KeyboardInterrupt (CTRL-C)
##
while repeat:
    try:
        ##
        ## Print basic temperature and humidity information.
        ## The temperature is in Degrees Celsius, the 
        ## Relative Humidity is in %. The accuracy of measurement
        ## should be +/- .3 degrees for tempeature and 
        ## +/- 2% for humidity
        ##
        print("\nTemperature: %0.1f C" % thSensor.temperature)
        print("RH: %0.1f %%" % thSensor.relative_humidity)
        sleep(5)
    except KeyboardInterrupt:
        ## Catch the keyboard interrupt and exit gracefully
        print("Exiting...")
        repeat = False
