from micropython import const
from machine import Pin, SPI
from utime import sleep_ms
import framebuf


ILI9341_DC_pin = const(7)
ILI9341_CS_pin = const(9)
ILI9341_BL_pin = const(8)
ILI9341_RST_pin = const(6)
ILI9341_SCK_pin = const(2)
ILI9341_MOSI_pin = const(3)

DAT = True
CMD = False

HIGH = True
LOW = False

ILI9341_NOP = const(0x00)
ILI9341_RESET = const(0x01)
ILI9341_READ_DISPLAY_IDENTIFICATION_INFORMATION = const(0x04)
ILI9341_READ_DISPLAY_STATUS = const(0x09)
ILI9341_READ_DISPLAY_POWER_MODE = const(0x0A)
ILI9341_READ_DISPLAY_MADCTL = const(0x0B)
ILI9341_READ_DISPLAY_PIXEL_FORMAT = const(0x0C)
ILI9341_READ_DISPLAY_IMAGE_FORMAT = const(0x0D)
ILI9341_READ_DISPLAY_SIGNAL_MODE = const(0x0E)
ILI9341_READ_DISPLAY_SELF_DIAGNOSTIC_RESULT = const(0x0F)
ILI9341_ENTER_SLEEP_MODE = const(0x10)
ILI9341_SLEEP_OUT = const(0x11)
ILI9341_PARTIAL_MODE_ON = const(0x12)
ILI9341_NORMAL_DISPLAY_MODE_ON = const(0x13)
ILI9341_DISPLAY_INVERSION_OFF = const(0x20)
ILI9341_DISPLAY_INVERSION_ON = const(0x21)
ILI9341_GAMMA = const(0x26)
ILI9341_DISPLAY_OFF = const(0x28)
ILI9341_DISPLAY_ON = const(0x29)
ILI9341_COLUMN_ADDR = const(0x2A)
ILI9341_PAGE_ADDR = const(0x2B)
ILI9341_GRAM = const(0x2C)
ILI9341_COLOR_SET = const(0x2D)
ILI9341_MEMORY_READ = const(0x2E)
ILI9341_PARTIAL_AREA = const(0x30)
ILI9341_VERTICAL_SCROLLING_DEFINITION = const(0x33)
ILI9341_TEARING_EFFECT_LINE_OFF = const(0x34)
ILI9341_TEARING_EFFECT_LINE_ON = const(0x35)
ILI9341_MAC = const(0x36)
ILI9341_VERTICAL_SCROLLING_START_ADDRESS = const(0x37)
ILI9341_IDLE_MODE_OFF = const(0x38)
ILI9341_IDLE_MODE_ON = const(0x39)
ILI9341_PIXEL_FORMAT = const(0x3A)
ILI9341_WMC = const(0x3C)
ILI9341_RMC = const(0x3E)
ILI9341_SET_TEAR_SCANLINE = const(0x44)
ILI9341_WDB = const(0x51)
ILI9341_READ_DISPLAY_BRIGHTNESS = const(0x52)
ILI9341_WCD = const(0x53)
ILI9341_READ_CTRL_DISPLAY = const(0x54)
ILI9341_WCABC = const(0x55)
ILI9341_RCABC = const(0x56)
ILI9341_WCABCMB = const(0x5E)
ILI9341_RCABCMB = const(0x5F)
ILI9341_RGB_INTERFACE = const(0xB0)
ILI9341_FRC = const(0xB1)
ILI9341_FRAME_CTRL_NM = const(0xB2)
ILI9341_FRAME_CTRL_IM = const(0xB3)
ILI9341_FRAME_CTRL_PM = const(0xB4)
ILI9341_BPC = const(0xB5)
ILI9341_DFC = const(0xB6)
ILI9341_ENTRY_MODE_SET = const(0xB7)
ILI9341_BACKLIGHT_CONTROL_1 = const(0xB8)
ILI9341_BACKLIGHT_CONTROL_2 = const(0xB9)
ILI9341_BACKLIGHT_CONTROL_3 = const(0xBA)
ILI9341_BACKLIGHT_CONTROL_4 = const(0xBB)
ILI9341_BACKLIGHT_CONTROL_5 = const(0xBC)
ILI9341_BACKLIGHT_CONTROL_6 = const(0xBD)
ILI9341_BACKLIGHT_CONTROL_7 = const(0xBE)
ILI9341_BACKLIGHT_CONTROL_8 = const(0xBF)
ILI9341_POWER1 = const(0xC0)
ILI9341_POWER2 = const(0xC1)
ILI9341_VCOM1 = const(0xC5)
ILI9341_VCOM2 = const(0xC7)
ILI9341_POWERA = const(0xCB)
ILI9341_POWERB = const(0xCF)
ILI9341_READ_ID1 = const(0xDA)
ILI9341_READ_ID2 = const(0xDB)
ILI9341_READ_ID3 = const(0xDC)
ILI9341_PGAMMA = const(0xE0)
ILI9341_NGAMMA = const(0xE1)
ILI9341_DTCA = const(0xE8)
ILI9341_DTCB = const(0xEA)
ILI9341_POWER_SEQ = const(0xED)
ILI9341_3GAMMA_EN = const(0xF2)
ILI9341_INTERFACE = const(0xF6)
ILI9341_PRC = const(0xF7)

X_Max = const(240)
Y_Max = const(320)

pixels = const(X_Max * Y_Max)


class TFT_ILI9341(framebuf.FrameBuffer):

    def __init__(self, ):
        self.MAX_X = Y_Max
        self.MAX_Y = X_Max

        self.PORTRAIT_1 = const(1)
        self.PORTRAIT_2 = const(2)
        self.LANDSCAPE_1 = const(3)
        self.LANDSCAPE_2 = const(4)

        self.BLACK = const(0x0000)
        self.BLUE = const(0x1F00)
        self.RED = const(0x00F8)
        self.GREEN = const(0xE007)
        self.CYAN = const(0xF81F)
        self.MAGENTA = const(0x7FE0)
        self.YELLOW = const(0x07FF)
        self.WHITE = const(0xFFFF)  

        self.ILI9341_CS = Pin(ILI9341_CS_pin, Pin.OUT)
        self.ILI9341_BL = Pin(ILI9341_BL_pin, Pin.OUT)
        self.ILI9341_RST = Pin(ILI9341_RST_pin, Pin.OUT)
        self.ILI9341_SCK = Pin(ILI9341_SCK_pin, Pin.OUT)
        self.ILI9341_MOSI = Pin(ILI9341_MOSI_pin, Pin.OUT)
        
        self.ILI9341_SPI = SPI(0, 60_000_000, polarity = False, phase = False, sck = self.ILI9341_SCK, mosi = self.ILI9341_MOSI, miso = None)
        
        self.ILI9341_DC = Pin(ILI9341_DC_pin, Pin.OUT)
        self.ILI9341_BL.on()

        self.buffer = bytearray(self.MAX_X * self.MAX_Y * 2)
        super().__init__(self.buffer, self.MAX_X, self.MAX_Y, framebuf.RGB565)

        self.TFT_init()


    def write(self, value, mode):
    	self.ILI9341_DC.value(mode)
        self.ILI9341_CS.value(LOW)
        self.ILI9341_SPI.write(bytearray([value]))
        self.ILI9341_CS.value(HIGH)
        
        
    def write_word(self, value, mode):
        lb = (value & 0x00FF)
        hb = ((value & 0xFF00) >> 0x08)
    	self.write(hb, mode)
    	self.write(lb, mode)


    def reset(self):
    	self.ILI9341_RST.value(LOW)
    	sleep_ms(20)
        self.ILI9341_RST.value(HIGH)


    def TFT_init(self):
    	self.reset()
    	self.write(ILI9341_RESET, CMD)
        sleep_ms(60)

        self.write(ILI9341_POWERA, CMD)
        self.write(0x39, DAT)
        self.write(0x2C, DAT)
        self.write(0x00, DAT)
        self.write(0x34, DAT)
        self.write(0x02, DAT)
        
        self.write(ILI9341_POWERB, CMD)
        self.write(0x00, DAT)
        self.write(0xC1, DAT)
        self.write(0x30, DAT)

        self.write(ILI9341_DTCA, CMD)
        self.write(0x85, DAT)
        self.write(0x00, DAT)
        self.write(0x78, DAT)

        self.write(ILI9341_DTCB, CMD)
        self.write(0x00, DAT)
        self.write(0x00, DAT)

        self.write(ILI9341_POWER_SEQ, CMD)
        self.write(0x64, DAT)
        self.write(0x03, DAT)
        self.write(0x12, DAT)
        self.write(0x81, DAT)

        self.write(ILI9341_PRC, CMD)
        self.write(0x20, DAT)

        self.write(ILI9341_POWER1, CMD)
        self.write(0x23, DAT)

        self.write(ILI9341_POWER2, CMD)
        self.write(0x10, DAT)

        self.write(ILI9341_VCOM1, CMD)
        self.write(0x3E, DAT)
        self.write(0x28, DAT)

        self.write(ILI9341_VCOM2, CMD)
        self.write(0x86, DAT)

        self.write(ILI9341_MAC, CMD)
        self.write(0x48, DAT)

        self.write(ILI9341_PIXEL_FORMAT, CMD)
        self.write(0x55, DAT)

        self.write(ILI9341_FRC, CMD)
        self.write(0x00, DAT)
        self.write(0x18, DAT)

        self.write(ILI9341_DFC, CMD)
        self.write(0x08, DAT)
        self.write(0x82, DAT)
        self.write(0x27, DAT)

        self.write(ILI9341_3GAMMA_EN, CMD)
        self.write(0x00, DAT)

        self.write(ILI9341_COLUMN_ADDR, CMD)
        self.write(0x00, DAT)
        self.write(0x00, DAT)
        self.write(0x00, DAT)
        self.write(0xEF, DAT)

        self.write(ILI9341_PAGE_ADDR, CMD)
        self.write(0x00, DAT)
        self.write(0x00, DAT)
        self.write(0x01, DAT)
        self.write(0x3F, DAT)

        self.write(ILI9341_GAMMA, CMD)
        self.write(0x01, DAT)

        self.write(ILI9341_PGAMMA, CMD)
        self.write(0x0F, DAT)
        self.write(0x31, DAT)
        self.write(0x2B, DAT)
        self.write(0x0C, DAT)
        self.write(0x0E, DAT)
        self.write(0x08, DAT)
        self.write(0x4E, DAT)
        self.write(0xF1, DAT)
        self.write(0x37, DAT)
        self.write(0x07, DAT)
        self.write(0x10, DAT)
        self.write(0x03, DAT)
        self.write(0x0E, DAT)
        self.write(0x09, DAT)
        self.write(0x00, DAT)

        self.write(ILI9341_NGAMMA, CMD)
        self.write(0x00, DAT)
        self.write(0x0E, DAT)
        self.write(0x14, DAT)
        self.write(0x03, DAT)
        self.write(0x11, DAT)
        self.write(0x07, DAT)
        self.write(0x31, DAT)
        self.write(0xC1, DAT)
        self.write(0x48, DAT)
        self.write(0x08, DAT)
        self.write(0x0F, DAT)
        self.write(0x0C, DAT)
        self.write(0x31, DAT)
        self.write(0x36, DAT)
        self.write(0x0F, DAT)

        self.write(ILI9341_SLEEP_OUT, CMD)
        sleep_ms(100)
        
        self.display_on_off(True)
        self.write(ILI9341_GRAM, CMD)

        self.set_rotation(self.LANDSCAPE_2)


    def display_on_off(self, status):
        if(status == True):
            self.write(ILI9341_DISPLAY_ON, CMD)

        else:
            self.write(ILI9341_DISPLAY_OFF, CMD)


    def set_rotation(self, rotation):
        self.write(ILI9341_MAC, CMD);
        
        if(rotation == self.PORTRAIT_1):
            self.write(0x58, DAT)

        elif(rotation == self.PORTRAIT_2):
            self.write(0x88, DAT)

        elif(rotation == self.LANDSCAPE_1):
            self.write(0x28, DAT)

        else:
            self.write(0xE8, DAT)

        if((rotation == self.PORTRAIT_1) or (rotation == self.PORTRAIT_2)):
            self.MAX_X = X_Max
            self.MAX_Y = Y_Max

        elif((rotation == self.LANDSCAPE_1) or (rotation == self.LANDSCAPE_2)):
            self.MAX_X = Y_Max
            self.MAX_Y = X_Max


    def set_display_window(self, x_1, y_1, x_2, y_2):
        self.write(ILI9341_COLUMN_ADDR, CMD)
        self.write_word(x_1, DAT)
        self.write_word((x_2 - 1), DAT)

        self.write(ILI9341_PAGE_ADDR, CMD)
        self.write_word(y_1, DAT)
        self.write_word((y_2 - 1), DAT)

        self.write(ILI9341_GRAM, CMD)


    def show(self):
        self.set_display_window(0, 0, self.MAX_X, self.MAX_Y)
        
        self.ILI9341_DC.value(DAT)
        self.ILI9341_CS.value(LOW)
        self.ILI9341_SPI.write(self.buffer)
        self.ILI9341_CS.value(HIGH)


    def colour_generator(self, r, g, b):
        r = (r & 0xF8)
        g = ((g & 0xFC) >> 2)
        b = ((b & 0xF8) >> 3)
        
        colour = r
        colour |= (b << 8)
        colour |= ((g & 0x38) >> 3)
        colour |= ((g & 0x07) << 13)
    
        return colour

