from machine import Pin, I2C
from time import sleep_ms
from ILI9341 import *
from BME680 import *
from bmp import image_data, image_width, image_height


LED = Pin(25, Pin.OUT)
i2c = I2C(id = 0, scl = Pin(21), sda = Pin(20), freq = 400000)

disp = TFT_ILI9341()
bme = BME680(i2c)

back_colour = disp.colour_generator(90, 90, 90)


def draw_icons():
    idx = 0
    for y in range(image_height):
        for x in range(image_width):
            high = image_data[idx]
            low = image_data[idx + 1]
            color = (low << 8) | high  # RGB565
            disp.pixel(x, y, color)
            idx += 2
            
            
def write_text(text, x, y, size, color):
        background = disp.pixel(x, y)
        info = []
        
        disp.text(text, x, y, color)
        for i in range(x, x + (8 * len(text))):
            for j in range(y, y + 8):
                px_color = disp.pixel(i, j)
                info.append((i, j, px_color)) if px_color == color else None
        
        disp.text(text, x, y, background)
       
        for px_info in info:
            disp.fill_rect(size*px_info[0] - (size-1)*x , size*px_info[1]
                          - (size-1)*y, size, size, px_info[2]) 



while(True):
    LED.toggle()
    T, P, RH, G, A, Td, G_index, iaq = bme.read()
    
    disp.fill(back_colour)
    draw_icons()
                          
    write_text("RP2350 RISC-V and BME680", 76, 2, 1, disp.WHITE)                      
    write_text(str("%2.2f deg C " %T), 72, 20, 2, disp.RED)
    write_text(str("%2.2f " %RH) + "% ", 72, 55, 2, disp.BLUE)
    write_text(str("%4.2f mBar " %P), 72, 90, 2, disp.GREEN)
    write_text(str("%2.2f deg C " %Td), 72, 135, 2, disp.CYAN)
    write_text(str("%2.2f " %iaq), 72, 175, 2, disp.MAGENTA)
    
    if((G_index <= 5)):
        write_text("Worst!", 72, 210, 2, disp.BLACK)        
    elif((G_index > 5) and (G_index < 25)):
        write_text("Bad.", 72, 210, 2, disp.RED)
    elif((G_index >= 25) and (G_index < 50)):
        write_text("Moderate.", 72, 210, 2, disp.YELLOW)
    elif((G_index >= 50) and (G_index < 75)):
        write_text("Good.", 72, 210, 2, disp.CYAN)
    else:
        write_text("Excellent.", 72, 210, 2, disp.GREEN)
        
    disp.show()
    print(T, P, RH, G, A, Td, G_index, iaq)
    
    sleep_ms(1000)

