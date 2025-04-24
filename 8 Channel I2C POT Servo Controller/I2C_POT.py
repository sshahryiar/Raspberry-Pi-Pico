from micropython import const
from machine import I2C
from time import sleep_us
from array import array


POT_I2C_ADDRESS = const(0x20)

POT_CH0_REG = const(0x50)
POT_CH1_REG = const(0x52)
POT_CH2_REG = const(0x54)
POT_CH3_REG = const(0x56)
POT_CH4_REG = const(0x58)
POT_CH5_REG = const(0x5A)
POT_CH6_REG = const(0x5C)
POT_CH7_REG = const(0x5E)


class I2C_POT():
    def __init__(self, _i2c):
        self.i2c = _i2c
        self.i2c_address = POT_I2C_ADDRESS
        
        
    def read_channel_raw(self, ch):
        value = 0
        value = self.i2c.readfrom_mem(self.i2c_address, (POT_CH0_REG + (2 * ch)), 2)
        return ((value[1] << 8) | value[0])


    def read_channel_avg(self, ch, avg_points = 4, sampling_delay = 100):
        i = 0
        avg = 0
        
        for i in range (0, avg_points, 1):
            avg += self.read_channel_raw(ch)
            sleep_us(sampling_delay)
        
        avg = int(avg / avg_points)
        return avg
    
    
    def read_all_channel_raw(self):
        i = 0
        raws = array('H', [0, 0, 0, 0, 0, 0, 0, 0, 0])   
        
        for i in range (0, 8, 1):
            raws[i] = self.read_channel_raw(i)
            
        return raws[0], raws[1], raws[2], raws[3], raws[4], raws[5], raws[6], raws[7]
    
    
    def read_all_channel_avg(self, avg_points = 4, sampling_delay = 100):
        i = 0
        avgs = array('H', [0, 0, 0, 0, 0, 0, 0, 0, 0])   
        
        for i in range (0, 8, 1):
            avgs[i] =  self.read_channel_avg(i, avg_points, sampling_delay)
            
        return avgs[0], avgs[1], avgs[2], avgs[3], avgs[4], avgs[5], avgs[6], avgs[7]
        