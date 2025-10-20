#
# TemperatureSensorIntegration.py
#

from gpiozero import Button, LED
from statemachine import StateMachine, State
from time import sleep
from datetime import datetime

import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import adafruit_ahtx0

from threading import Thread

DEBUG = True

# 16x2 LCD formatting targets (exact width)
LCD_COLS = 16
LCD_ROWS = 2
# Time format chosen to be exactly 16 chars: "Oct 05  12:34:56"
TIME_FMT = "%b %d  %H:%M:%S"  # 3+1+2+2+8 = 16

class ManagedDisplay():
    def __init__(self):
        # LCD pin mapping (BCM)
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        self.lcd_columns = LCD_COLS
        self.lcd_rows = LCD_ROWS

        self.lcd = characterlcd.Character_LCD_Mono(
            self.lcd_rs, self.lcd_en,
            self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7,
            self.lcd_columns, self.lcd_rows
        )
        self.lcd.clear()

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def clear(self):
        self.lcd.clear()

    def updateScreen(self, line1, line2):
        """
        Update the LCD with two lines, each padded/truncated to 16 chars,
        with a single write to avoid flicker.
        """
        l1 = (line1[:LCD_COLS]).ljust(LCD_COLS)
        l2 = (line2[:LCD_COLS]).ljust(LCD_COLS)
        self.lcd.clear()
        self.lcd.message = f"{l1}\n{l2}"

class TempMachine(StateMachine):
    "State machine to manage temperature scale and rendering"

    # LEDs available to indicate state
    redLight = LED(18)
    blueLight = LED(23)

    scale1 = 'F'
    scale2 = 'C'
    activeScale = scale2  # default 'C'

    Celsius = State(initial=True)
    Fahrenheit = State()

    screen = ManagedDisplay()

    # AHTx0 sensor on I2C (Qwiic), default address 0x38
    i2c = board.I2C()
    thSensor = adafruit_ahtx0.AHTx0(i2c)

    # Button-driven transition (C <-> F)
    cycle = (Celsius.to(Fahrenheit) | Fahrenheit.to(Celsius))

    def on_enter_Celsius(self):
        self.activeScale = self.scale2
        if DEBUG:
            print("* Changing state to Celsius")

    def on_enter_Fahrenheit(self):
        self.activeScale = self.scale1
        if DEBUG:
            print("* Changing state to Fahrenheit")

    def processButton(self):
        if DEBUG:
            print('*** processButton')
        self.send("cycle")

    def run(self):
        myThread = Thread(target=self.displayTemp, daemon=True)
        myThread.start()

    def getFahrenheit(self):
        t = self.thSensor.temperature
        return ((9.0/5.0) * t) + 32.0

    def getCelsius(self):
        return self.thSensor.temperature

    def getRH(self):
        return self.thSensor.relative_humidity

    endDisplay = False

    def displayTemp(self):
        while not self.endDisplay:
            # Line 1: current date/time (exactly 16 chars)
            line1 = datetime.now().strftime(TIME_FMT)

            # Line 2: temperature + scale, humidity as a percentage
            if self.activeScale == 'C':
                # e.g., "T:23.4C H:45.0%"
                line2 = f"T:{self.getCelsius():0.1f}C H:{self.getRH():0.1f}%"
            else:
                # e.g., "T:74.1F H:45.0%"
                line2 = f"T:{self.getFahrenheit():0.1f}F H:{self.getRH():0.1f}%"

            self.screen.updateScreen(line1, line2)
            sleep(1)

        # Cleanup the display
        self.screen.cleanupDisplay()

# Initialize state machine and start the display thread
tempMachine = TempMachine()
tempMachine.run()

# Button on GPIO 24. Default gpiozero Button uses internal pull-up.
# Wire the button between GPIO24 and GND.
greenButton = Button(24)  # If wired to 3V3 with a pull-down, use Button(24, pull_up=False)
greenButton.when_pressed = tempMachine.processButton

repeat = True
while repeat:
    try:
        if DEBUG:
            print("Killing time in a loop...")
        sleep(20)
    except KeyboardInterrupt:
        print("Cleaning up. Exiting...")
        repeat = False
        tempMachine.endDisplay = True
        sleep(1)
