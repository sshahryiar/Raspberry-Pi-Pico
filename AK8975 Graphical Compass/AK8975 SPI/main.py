from micropython import const
from machine import I2C, SoftSPI, Pin
from SSD1306_I2C import *
from AK8975 import *
from time import sleep_ms
import math


scale_factor = const(12)
scale_factor_p = const(3)


conv_factor = 0.0174532925
pi_by_2 = 1.570796327


state = False 


LED = Pin(17, Pin.OUT)
Button = Pin(29, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl = Pin(27), sda = Pin(26), freq = 400000)
spi = SoftSPI(100000, polarity = True, phase = True, sck = Pin(6), mosi = Pin(7), miso = Pin(8))
        

oled = OLED1306(i2c)
compass = AK8975(spi, 9)

oled.fill(0)
oled.show()

#compass.calibrate();


def draw_background():
    oled.ellipse(32, 36, 1, 1, oled.WHITE, True)
    oled.ellipse(32, 36, 24, 24, oled.WHITE, False) 
    oled.ellipse(32, 36, 26, 26, oled.WHITE, False)  
    oled.text("RP2040 & AK8975", 1, 1, oled.WHITE)
    
    
def draw_pointer(heading_in_degrees):
    global state
    
    heading_in_radians = (heading_in_degrees * conv_factor)
    
    h = int(scale_factor * math.sin(heading_in_radians))
    v = int(scale_factor * math.cos(heading_in_radians))
    
    if(state):
        if((heading > 0) and (heading <= 90)):
            hn = (32 + h)
            vn = (30 - v)        
            hs = (26 - h)
            vs = (38 + v)
            
        elif((heading > 90) and (heading <= 180)):
            hn = (32 + h)
            vn = (36 - v)        
            hs = (26 - h)
            vs = (30 + v)
      
        elif((heading > 180) and (heading <= 270)):
            hn = (26 + h)
            vn = (36 - v)        
            hs = (32 - h) 
            vs = (30 + v)
            
        else:
            hn = (26 + h)
            vn = (30 - v)        
            hs = (32 - h)
            vs = (38 + v)

          
        oled.text("N", hn, vn, oled.WHITE)
        oled.text("S", hs, vs, oled.WHITE)
    
    else:
        oled.line(32, 36, (32 + h), (36 - v), oled.WHITE)
    
        vp = int(scale_factor_p * math.cos((heading_in_radians - pi_by_2)))
        hp = int(scale_factor_p * math.sin((heading_in_radians - pi_by_2)))
        oled.line(32, 36, (32 - hp), (36 + vp), oled.WHITE)
        oled.line(32, 36, (32 + hp), (36 - vp), oled.WHITE)
         
        oled.line((32 + h), (36 - v), (32 + hp), (36 - vp),  oled.WHITE)
        oled.line((32 - h), (36 + v), (32 + hp), (36 - vp),  oled.WHITE)
        oled.line((32 + h), (36 - v), (32 - hp), (36 + vp),  oled.WHITE)
        oled.line((32 - h), (36 + v), (32 - hp), (36 + vp),  oled.WHITE)
        
    oled.text(str("%3.1f N " %heading_in_degrees), 64, 32)
    oled.show()
    


while(True):
    try:
        LED.on()
        
        if(Button.value() == False):
            while(Button.value() == False):
                LED.on()
                sleep_ms(40)
                LED.off()
                sleep_ms(40)
            state = not state
        
        x, y, z = compass.read_raw_magnetic_data()
        print(f"Raw: X = {x:04d}, Y = {y:04d}, Z = {z:04d}")
        
        x_uT, y_uT, z_uT = compass.read()
        print(f"Calibrated: X = {x_uT:4.2f} uT, Y = {y_uT:4.2f} uT, Z = {z_uT:4.2f} uT")
        
        heading = compass.heading(y, z)
        print(f"Heading: {heading:3.1f}°")

        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(heading / 45) % 8
        print(f"Direction: {directions[index]}")

        oled.fill(0x00)
        draw_background()
        draw_pointer(heading)
        sleep_ms(200)
        LED.off()
        sleep_ms(200)
        
    except Exception as e:
        print(f"Error: {e}") 
    print("")
    sleep_ms(1000)
