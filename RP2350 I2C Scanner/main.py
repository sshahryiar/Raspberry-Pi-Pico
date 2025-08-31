from machine import Pin, I2C
from ILI9341 import TFT_ILI9341


i = 0


i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)
tft = TFT_ILI9341()
tft.fill(tft.BLACK)
tft.show()



device_map = {}
with open('I2C_devices.csv') as f:
    for line in f:
        parts = line.strip().split(',')
        if(len(parts) >= 2):
            addr = int(parts[0], 16)  
            device_map[addr] = parts[1] 


found = i2c.scan()


tft.fill(tft.BLACK)
string = "RP2350 Raspberry Pi PICO 2 I2C Scanner"
tft.text(string, 1, 1, tft.CYAN)
print(string)

string = "Found Device(s):"
tft.text(string, 1, 15, tft.CYAN)
print(string)


if not found:
    string = "No I2C devices found!"
    print(string)
    tft.text(string, 1, 35, tft.RED)
    
else:
    tft.text("Found Device(s)", 1, 15, tft.CYAN)
    for addr in found:    
        if addr in device_map:
            string = f"0x{addr:02X} > {device_map[addr]}"
            color = tft.WHITE
            
        else:
            string = f"0x{addr:02X} > Unknown Device!"
            color = tft.YELLOW
        
        print(string)
        tft.text(string, 1, (35 + i), color)
        i += 11
        
tft.show()
