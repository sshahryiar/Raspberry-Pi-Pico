from micropython import const
from machine import Pin


MAX72xx_NOP = const(0x00)
MAX72xx_decode_mode_reg = const(0x09)
MAX72xx_intensity_reg = const(0x0A)
MAX72xx_scan_limit_reg = const(0x0B)
MAX72xx_shutdown_reg = const(0x0C)
MAX72xx_display_test_reg = const(0x0F)

MAX72xx_shutdown_cmd = const(0x00)
MAX72xx_run_cmd = const(0x01)

MAX72xx_no_test_cmd = const(0x00)
MAX72xx_test_cmd = const(0x01)
                             
MAX72xx_digit_0_only = const(0x00)
MAX72xx_digit_0_to_1 = const(0x01)
MAX72xx_digit_0_to_2 = const(0x02)
MAX72xx_digit_0_to_3 = const(0x03)
MAX72xx_digit_0_to_4 = const(0x04)
MAX72xx_digit_0_to_5 = const(0x05)
MAX72xx_digit_0_to_6 = const(0x06)
MAX72xx_digit_0_to_7 = const(0x07)
                                                  
MAX72xx_No_decode_for_all = const(0x00)
MAX72xx_Code_B_decode_digit_0 = const(0x01)
MAX72xx_Code_B_decode_digit_0_to_3 = const(0x0F)	
MAX72xx_Code_B_decode_for_all = const(0xFF)


class MAX72xx():
    def __init__(self, _spi, _csn):
        self.DIG0 = const(0x08)
        self.DIG1 = const(0x07)
        self.DIG2 = const(0x06)
        self.DIG3 = const(0x05)
        self.DIG4 = const(0x04)
        self.DIG5 = const(0x03)
        self.DIG6 = const(0x02)
        self.DIG7 = const(0x01)
        
        self.spi = _spi
        self.csn = Pin(_csn, Pin.OUT)
        self.buffer = bytearray(0x02)
        self.init()
        
        
    def init(self):
        self.csn.on()
        self.write(MAX72xx_shutdown_reg, MAX72xx_run_cmd)
        self.write(MAX72xx_decode_mode_reg, MAX72xx_Code_B_decode_for_all)
        self.write(MAX72xx_scan_limit_reg, MAX72xx_digit_0_to_7)
        self.write(MAX72xx_intensity_reg, 0x15)
        self.clear()
        
    
    def clear(self):
        for i in range(0x00, 0x09):
            self.write(i, 0x7F)
        
        
    def write(self, address, value):
        self.buffer[0x00] = address
        self.buffer[0x01] = value
        
        self.csn.off()
        self.spi.write(self.buffer)
        self.csn.on()