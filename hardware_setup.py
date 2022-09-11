# ili9341_pico.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# As written, supports:
# ili9341 240x320 displays on Pi Pico
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING
# Pico      Display
# GPIO Pin
# 3v3  36   Vin
# IO6   9   CLK  Hardware SPI0
# IO7  10   DATA (AKA SI MOSI)
# IO8  11   DC
# IO9  12   Rst
# Gnd  13   Gnd
# IO10 14   CS

# Pushbuttons are wired between the pin and Gnd
# Pico pin  Meaning
# 16        Operate current control
# 17        Decrease value of current control
# 18        Select previous control
# 19        Select next control
# 20        Increase value of current control

from machine import Pin, I2C, freq
import gc

from drivers.ssd1306.ssd1306 import SSD1306_I2C as SSD
#freq(250_000_000)  # RP2 overclock

# Create and export an SSD instance
i2c = I2C(0, sda=Pin(12), scl=Pin(13))
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(128, 64, i2c)
gc.collect()
from gui.core.ugui import Display
# quiet()
# Create and export a Display instance
# Define control buttons
nxt = Pin(11, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(14, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(10, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(28, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(1, Pin.IN, Pin.PULL_UP)  # Decrease control's value
# display = Display(ssd, nxt, sel, prev)  # 3-button mode
display = Display(ssd, nxt, sel, prev, increase, decrease)  # Encoder mode
