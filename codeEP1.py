import board, busio, displayio, time
import digitalio
from time import sleep

import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_st7789 import ST7789

import terminalio
import os, sys
import gc

import terminalio
import microcontroller

#----ST7789
tft_cs = board.CE0
tft_dc = board.D24
tft_res = board.D25

spi_mosi = board.D10 
spi_clk  = board.D9 
displayio.release_displays()

spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_res,baudrate=31250000)
display = ST7789(display_bus, rotation=90, width=320, height=240)

splash = displayio.Group()
display.root_group = splash

pic_0 = displayio.OnDiskBitmap("ss1.bmp")
pic_1 = displayio.OnDiskBitmap("ss2.bmp")
pic_2 = displayio.OnDiskBitmap("ss3.bmp")
pic_3 = displayio.OnDiskBitmap("ss4.bmp")

group = displayio.Group()
display.root_group = group

text = "RaspberryPi ZERO/NoOs"

label_text = label.Label(terminalio.FONT, text=text, color=0xFFFFFF,x=10, y=10)
label_text.anchor_point = (1.0, 0.0)
label_text.anchored_position = (280, 155)
label_text.scale = (2)

group.append(label_text)
display.root_group = group

while True:
    
    tile_grid = displayio.TileGrid(pic_0, pixel_shader=pic_0.pixel_shader)
    group.append(tile_grid)
    display.root_group = group
    sleep(10)
    group.remove(tile_grid)
    sleep(.1)    
    
    tile_grid = displayio.TileGrid(pic_1, pixel_shader=pic_0.pixel_shader)
    group.append(tile_grid)
    display.root_group = group
    sleep(10)
    group.remove(tile_grid)
    sleep(.1)
    
    tile_grid = displayio.TileGrid(pic_2, pixel_shader=pic_0.pixel_shader)
    group.append(tile_grid)
    display.root_group = group
    sleep(10)
    group.remove(tile_grid)
    sleep(.1)
    
    tile_grid = displayio.TileGrid(pic_3, pixel_shader=pic_0.pixel_shader)
    group.append(tile_grid)
    display.root_group = group
    sleep(10)
    group.remove(tile_grid)
    sleep(.1)  


gc.collect()
print("mem: ", gc.mem_free())
