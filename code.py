import board
import time
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import adafruit_lis331

displayio.release_displays()

oled_reset = board.D9

# Use for I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=oled_reset)

# Use for SPI
# spi = board.SPI()
# oled_cs = board.D5
# oled_dc = board.D6
# display_bus = displayio.FourWire(spi, command=oled_dc, chip_select=oled_cs,
#                                 reset=oled_reset, baudrate=1000000)

WIDTH = 128
HEIGHT = 32  # Change to 64 if needed
BORDER = 0

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.show(splash)

# color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
# color_palette = displayio.Palette(1)
# color_palette[0] = 0xFFFFFF  # White
#
# bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
# splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)



lis = adafruit_lis331.H3LIS331(i2c)
# lis = adafruit_lis331.LIS331HH(i2c)

# lis.hpf_reference = 1
# lis.enable_hpf(True, cutoff=adafruit_lis331.RateDivisor.ODR_DIV_100, use_reference=True)

max_val = 0  # our current max acceleration value
ranOnce = False  # Check if loop has run at least once
swing_time = 3000

while True:
    # accel_mag >>= 4  # bit shift correction
    accelx = lis.acceleration[0]-24
    accely = lis.acceleration[1]-30
    accelz = lis.acceleration[2]+37

    # Magnitude
    accel_mag = (accelx ** 2 + accely ** 2 + accelz ** 2) ** 0.5
    local_max = accel_mag

    if accel_mag > max_val*.1:
        firstLoop = True
        for x in range(swing_time):
            accelx = lis.acceleration[0]-24
            accely = lis.acceleration[1]-30
            accelz = lis.acceleration[2]+37
            # Magnitude
            accel_mag = (accelx ** 2 + accely ** 2 + accelz ** 2) ** 0.5
            if firstLoop:
                if accel_mag > local_max:
                    local_max = accel_mag

                local_text = "Cur:" + str(round(local_max, 3)) + " m/s^2"
                text_area = label.Label(terminalio.FONT, text=local_text, color=0xFFFFFF, x=20, y=19)
                splash.append(text_area)
                firstLoop = False
            if accel_mag > local_max:
                local_max = accel_mag
                local_text = "Cur:" + str(round(local_max, 3)) + " m/s^2"
                splash.pop()
                text_area = label.Label(terminalio.FONT, text=local_text, color=0xFFFFFF, x=20, y=19)
                splash.append(text_area)
        splash.pop()
    else:
        continue


    # only display greatest value on accelerometer (which will be axe swing)
    if local_max > max_val:
        max_val = local_max
        max_text = "Max:" + str(round(max_val, 3)) + " m/s^2"
        # text = str(int(sum(accelx)/len(accelx))) + " " + str(int(sum(accely)/len(accely))) + "\n" + str(int(sum(accelz)/len(accelz)))

    else:
        continue  # re-run the loop b/c accel value hasn't changed

    if ranOnce:
        # remove what was previously displayed on screen to update accel value
        splash.pop()

    text_area = label.Label(terminalio.FONT, text=max_text, color=0xFFFFFF, x=20, y=4)

    splash.append(text_area)
    ranOnce = True
    # time.sleep(0.5)
