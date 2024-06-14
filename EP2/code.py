import board
import busio
import displayio
import time
import digitalio
import gc
from adafruit_display_text import label
from adafruit_st7789 import ST7789
import terminalio
from displayio_gauge import Gauge
import adafruit_ads1x15.ads1115 as ADS
import adafruit_ads1x15.analog_in as AnalogIn

###############################################
# Create the I2C bus
###############################################
SDA = board.D2
SCL = board.D3
i2c = busio.I2C(SCL, SDA)
# Create the ADC object using the I2C bus
ads_48 = ADS.ADS1115(i2c, address=0x48)

# Create single-ended input objects for each channel
s1 = AnalogIn.AnalogIn(ads_48, ADS.P0)
s2 = AnalogIn.AnalogIn(ads_48, ADS.P1)
s3 = AnalogIn.AnalogIn(ads_48, ADS.P2)
s4 = AnalogIn.AnalogIn(ads_48, ADS.P3)

#----ST7789
tft_cs = board.CE0
tft_dc = board.D24
tft_res = board.D25

spi_mosi = board.D10 
spi_clk  = board.D9 
displayio.release_displays()

spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_res, baudrate=31250000)
display = ST7789(display_bus, rotation=90, width=320, height=240)

splash = displayio.Group()
display.root_group = splash

pic_0 = displayio.OnDiskBitmap("voltframe.bmp")

bar_grid1 = displayio.TileGrid(pic_0, pixel_shader=pic_0.pixel_shader, x=0, y=0)
bar_grid2 = displayio.TileGrid(pic_0, pixel_shader=pic_0.pixel_shader, x=162, y=0)
bar_grid3 = displayio.TileGrid(pic_0, pixel_shader=pic_0.pixel_shader, x=0, y=122)
bar_grid4 = displayio.TileGrid(pic_0, pixel_shader=pic_0.pixel_shader, x=162, y=122)
group = displayio.Group()
display.root_group = group

label1 = label.Label(terminalio.FONT, text="V1", color=0xFFFFFF, x=10, y=10)
label1.anchor_point = (1.0, 0.0)
label1.anchored_position = (92, 85)
label1.scale = (2)

label2 = label.Label(terminalio.FONT, text="V2", color=0xFFFFFF, x=10, y=10)
label2.anchor_point = (1.0, 0.0)
label2.anchored_position = (248, 85)
label2.scale = (2)

label3 = label.Label(terminalio.FONT, text="V3", color=0xFFFFFF, x=10, y=10)
label3.anchor_point = (1.0, 0.0)
label3.anchored_position = (92, 205)
label3.scale = (2)

label4 = label.Label(terminalio.FONT, text="V4", color=0xFFFFFF, x=10, y=10)
label4.anchor_point = (1.0, 0.0)
label4.anchored_position = (248, 205)
label4.scale = (2)




label_text1 = label.Label(terminalio.FONT, text="0.00V", color=0xFFFFFF, x=10, y=10)
label_text1.anchor_point = (1.0, 0.0)
label_text1.anchored_position = (110, 55)
label_text1.scale = (2)

label_text2 = label.Label(terminalio.FONT, text="0.00V", color=0xFFFFFF, x=10, y=10)
label_text2.anchor_point = (1.0, 0.0)
label_text2.anchored_position = (265, 55)
label_text2.scale = (2)

label_text3 = label.Label(terminalio.FONT, text="0.00V", color=0xFFFFFF, x=10, y=10)
label_text3.anchor_point = (1.0, 0.0)
label_text3.anchored_position = (110, 175)
label_text3.scale = (2)

label_text4 = label.Label(terminalio.FONT, text="0.00V", color=0xFFFFFF, x=10, y=10)
label_text4.anchor_point = (1.0, 0.0)
label_text4.anchored_position = (265, 175)
label_text4.scale = (2)

gauge1 = Gauge(
    x=72,
    y=60,
    radius=50,
    thickness=10,
    level=0,
    outline_color=0xFFFFFF,
    foreground_color=0x00FF00,
    background_color=0x000000,
)

gauge2 = Gauge(
    x=232,
    y=60,
    radius=50,
    thickness=10,
    level=0,
    outline_color=0xFFFFFF,
    foreground_color=0x00FF00,
    background_color=0x000000,
)

gauge3 = Gauge(
    x=72,
    y=180,
    radius=50,
    thickness=10,
    level=0,
    outline_color=0xFFFFFF,
    foreground_color=0x00FF00,
    background_color=0x000000,
)

gauge4 = Gauge(
    x=232,
    y=180,
    radius=50,
    thickness=10,
    level=0,
    outline_color=0xFFFFFF,
    foreground_color=0x00FF00,
    background_color=0x000000,
)

group.append(bar_grid1)
group.append(bar_grid2)
group.append(bar_grid3)
group.append(bar_grid4)

group.append(gauge1)
group.append(gauge2)
group.append(gauge3)
group.append(gauge4)
group.append(label_text1)
group.append(label_text2)
group.append(label_text3)
group.append(label_text4)
group.append(label1)
group.append(label2)
group.append(label3)
group.append(label4)
display.root_group = group

while True:
    try:
        voltages = [s1.voltage, s2.voltage, s3.voltage, s4.voltage]
        
        print("{:>5.2f}\t{:>5.2f}\t{:>5.2f}\t{:>5.2f}".format(*voltages))
        
        # Update labels with voltage values
        label_text1.text = "{:.2f}V".format(voltages[0])
        label_text2.text = "{:.2f}V".format(voltages[1])
        label_text3.text = "{:.2f}V".format(voltages[2])
        label_text4.text = "{:.2f}V".format(voltages[3])
        
        # Update gauge levels (assuming max voltage is 5V and scaling to 100)
        gauge1.level = int((voltages[0] / 5.0) * 100)
        gauge2.level = int((voltages[1] / 5.0) * 100)
        gauge3.level = int((voltages[2] / 5.0) * 100)
        gauge4.level = int((voltages[3] / 5.0) * 100)
        
        time.sleep(0.4)
        gc.collect()  # Collect garbage to free up memory
    except Exception as e:
        print("Error:", e)
        # Handle the error or reset the connection

    gc.collect()  # Collect garbage to free up memory at the end of each loop
    print("mem: ", gc.mem_free())


