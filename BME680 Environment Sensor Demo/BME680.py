from machine import I2C
from micropython import const
from time import sleep_ms, ticks_diff, ticks_ms


BME680_DEFAULT_I2C_ADDRESS = 0x77

BME680_GAS_HEATER_REG_0 = const(0x5A)
BME680_GAS_DURATION_REG_0 = const(0x64)
BME680_CTRL_GAS_REG_1 = const(0x70)
BME680_CTRL_GAS_REG_2 = const(0x71)
BME680_CTRL_HUM_REG = const(0x72)
BME680_SPI_REG = const(0x73)
BME680_CTRL_MEAS_REG = const(0x74)
BME680_CONFIG_REG = const(0x75)
BME680_STATUS_REG = const(0x1D)
BME680_CHIPID_REG = const(0xD0)
BME680_SOFTRESET_REG = const(0xE0)
BME680_COEFF_START_ADDR_1 = const(0x89)
BME680_COEFF_START_ADDR_2 = const(0xE1)

BME680_RES_HEAT_VAL_ADDR = const(0x00)
BME680_RES_HEAT_RANGE_ADDR = const(0x02)
BME680_RANGE_SW_ERR_ADDR = const(0x04)

BME680_CHIP_ID = const(0x61)
BME680_RESET_CODE = const(0xB6)
BME680_RUN_GAS = const(0x10)

BME680_IIR_FILTER_OFF = const(0)
BME680_IIR_FILTER_2 = const(1)
BME680_IIR_FILTER_4 = const(2)
BME680_IIR_FILTER_8 = const(3)
BME680_IIR_FILTER_16 = const(4)
BME680_IIR_FILTER_32 = const(5)
BME680_IIR_FILTER_64 = const(6) 
BME680_IIR_FILTER_128 = const(7)

BME680_OVERSAMPLING_SKIP = const(0)
BME680_OVERSAMPLING_X1 = const(1)
BME680_OVERSAMPLING_X2 = const(2)
BME680_OVERSAMPLING_X4 = const(3)
BME680_OVERSAMPLING_X8 = const(4)
BME680_OVERSAMPLING_X16 = const(5)


LUT_1 = (2147483647.0, 2147483647.0, 2147483647.0, 2147483647.0, 2147483647.0,
         2126008810.0, 2147483647.0, 2130303777.0, 2147483647.0, 2147483647.0,
         2143188679.0, 2136746228.0, 2147483647.0, 2126008810.0, 2147483647.0,
         2147483647.0)

LUT_2 = (4096000000.0, 2048000000.0, 1024000000.0, 512000000.0, 255744255.0, 127110228.0,
         64000000.0, 32258064.0, 16016016.0, 8000000.0, 4000000.0, 2000000.0, 1000000.0,
         500000.0, 250000.0, 125000.0)


class BME680:
    
    def __init__(self, _i2c,
                 _i2c_address = BME680_DEFAULT_I2C_ADDRESS,
                 sample_time = 1000,
                 IIR_Filter = BME680_IIR_FILTER_4,
                 _P_OS = BME680_OVERSAMPLING_X4,
                 _T_OS = BME680_OVERSAMPLING_X8,
                 _H_OS = BME680_OVERSAMPLING_X2,
                 _gas_baseline = 100000,
                 pres = 1013.25):
        
        self.i2c = _i2c
        self.i2c_addr = _i2c_address
        
        self.soft_reset()
        sleep_ms(100)
        
        chip_ID = self.multibyte_read(BME680_CHIPID_REG, 1)[0]
        print("Chip ID: " + str('0x%02X' %chip_ID));
        
        if(chip_ID != BME680_CHIP_ID):
            print("BME680 not detected!\r\n")
        else:
            print("BME680 initializing....\r\n")
            
            self.cal_T1 = 0
            self.cal_T2 = 0
            self.cal_T3 = 0                       
            self.cal_RH1 = 0
            self.cal_RH2 = 0
            self.cal_RH3 = 0
            self.cal_RH4 = 0
            self.cal_RH5 = 0
            self.cal_RH6 = 0
            self.cal_RH7 = 0            
            self.cal_G1 = 0
            self.cal_G2 = 0
            self.cal_G3 = 0
            self.cal_P1 = 0
            self.cal_P2 = 0
            self.cal_P3 = 0
            self.cal_P4 = 0
            self.cal_P5 = 0
            self.cal_P6 = 0
            self.cal_P7 = 0
            self.cal_P8 = 0
            self.cal_P9 = 0
            self.cal_P10 = 0  
            self.heat_range = 0
            self.heat_val = 0
            self.sw_err = 0
            self.past_reading_tick = 0
            self.read_interval = sample_time
            self.filter = IIR_Filter
            self.P_OS = _P_OS
            self.T_OS = _T_OS
            self.H_OS = _H_OS
            self.gas_baseline = _gas_baseline
            self.sea_level_pressure = pres
            
            self.read_calibration()
            self.write(BME680_GAS_HEATER_REG_0, 0x73)
            self.write(BME680_GAS_DURATION_REG_0, 0x65)
        
        
    def soft_reset(self):
        self.write(BME680_SOFTRESET_REG, BME680_RESET_CODE)
        
        
    def make_word(self, HB, LB):
        return ((HB << 0x08) | LB)
    
    
    def write(self, reg, value):
        if not type(value) is bytearray:
            value = bytearray([value])
        
        self.i2c.writeto_mem(self.i2c_addr, reg, value)
                
            
    def multibyte_read(self, reg, no_of_bytes):
        retval = bytearray(no_of_bytes)
        self.i2c.readfrom_mem_into(self.i2c_addr, (reg & 0xFF), retval)
        return retval
    
    
    def make_signed_byte(self, value):
        if(value > 127):
            value -= 256
        return value
    
    
    def make_signed_word(self, value):
        if(value > 32767):
            value -= 65536
        return value
    
    
    def read(self):
        data_update = False
        
        if(ticks_diff(ticks_ms(), self.past_reading_tick) > self.read_interval):
            self.write(BME680_CONFIG_REG, (self.filter << 2))
            self.write(BME680_CTRL_MEAS_REG, ((self.T_OS << 5) | (self.P_OS << 2)))
            self.write(BME680_CTRL_HUM_REG, self.H_OS)
            self.write(BME680_CTRL_GAS_REG_2, BME680_RUN_GAS)
            ctrl_meas = self.multibyte_read(BME680_CTRL_MEAS_REG, 1)[0]
            ctrl_meas = ((ctrl_meas & 0xFC) | 0x01)            
            self.write(BME680_CTRL_MEAS_REG, ctrl_meas)
            
            while(not data_update):
                values = self.multibyte_read(BME680_STATUS_REG, 15)
                data_update = (values[0] & 0x80)
                sleep_ms(6)
            
            ADC_P = ((values[2] << 12) | (values[3] << 4) | (values[4] >> 4))            
            ADC_T = ((values[5] << 12) | (values[6] << 4) | (values[7] >> 4))
            ADC_RH = ((values[8] << 8) | values[9])
            ADC_G = ((values[13] << 2) | (values[14] >> 6))
            gas_range = (values[14] & 0x0F)
            
            var1 = ((ADC_T / 8) - (self.cal_T1 * 2))
            var2 = ((var1 * self.cal_T2) / 2048)
            var3 = (((var1 / 2) * (var1 / 2)) / 4096)
            var3 = ((var3 * self.cal_T3 * 16) / 16384)
            t_fine = int(var2 + var3)
            temp_scaled = (((t_fine * 5) + 128) / 256)
            T = (temp_scaled / 100)
            T = round(T, 2)
            
            var1 = ((t_fine / 2) - 64000)
            var2 = (((var1 / 4) * (var1 / 4)) / 2048)
            var2 = (var2 * self.cal_P6) / 4
            var2 = (var2 + (var1 * self.cal_P5 * 2))
            var2 = ((var2 / 4) + (self.cal_P4 * 65536))
            var1 = (((((var1 / 4) * (var1 / 4)) / 8192)
                     * (self.cal_P3 * 32) / 8)
                    + ((self.cal_P2 * var1) / 2))
            var1 = (var1 / 262144)
            var1 = (((32768 + var1) * self.cal_P1) / 32768)
            P = (1048576 - ADC_P)
            P = ((P - (var2 / 4096)) * 3125)
            P = ((P / var1) * 2)
            var1 = ((self.cal_P9 * (((P / 8) * (P / 8)) / 8192)) / 4096)
            var2 = (((P / 4) * self.cal_P8) / 8192)
            var3 = ((((P / 256) ** 3) * self.cal_P10) / 131072)
            P += ((var1 + var2 + var3 + (self.cal_P7 * 128)) / 16)
            P /= 100
            P = round(P, 2)
            
            A = 44330 * (1.0 - pow(P / self.sea_level_pressure, 0.1903))
            A = round(A, 2)
            
            var1 = ((ADC_RH - (self.cal_RH1 * 16)) - ((temp_scaled * self.cal_RH3) / 200))
            var2 = ((self.cal_RH2 * (((temp_scaled * self.cal_RH4) / 100)
                                   + (((temp_scaled * ((temp_scaled * self.cal_RH5) / 100))
                                       / 64) / 100) + 16384)) / 1024)
            var3 = (var1 * var2)
            var4 = (self.cal_RH6 * 128)
            var4 = ((var4 + ((temp_scaled * self.cal_RH7) / 100)) / 16)
            var5 = (((var3 / 16384) * (var3 / 16384)) / 1024)
            var6 = ((var4 * var5) / 2)
            RH = ((((var3 + var6) / 1024) * 1000) / 4096)
            RH /= 1000
            
            if(RH >= 100):
              RH = 100
            if(RH <= 0):
              RH = 0
              
            RH = round(RH, 2)
            
            var1 = (((1340 + (5 * self.sw_err)) * (LUT_1[gas_range])) / 65536)
            var2 = (((ADC_G * 32768) - 16777216) + var1)
            var3 = ((LUT_2[gas_range] * var1) / 512)
            G = ((var3 + (var2 / 2)) / var2)
            G = round(G, 2)
            
            Td = (T - ((100 - RH) / 5))
            Td = round(Td, 2)
            
            if(G >= 100000):
                G_index = 100
            
            elif((G >= 50000) and (G < 100000)):
                G_index = 75
                
            elif((G >= 10000) and (G < 50000)):
                G_index = 50
                
            elif((G >= 1000) and (G < 10000)):
                G_index = 25
            
            else:
                G_index = 5
                
            g_score = (min((G / self.gas_baseline), 1) * 100)
            rh_score = max(0, (100 - abs(RH - 40) * 2))
            combined_score = ((0.75 * g_score) + (0.25 * rh_score))
            iaq = round(max(0, min(500, (500 - (combined_score * 5)))))
            
            self.past_reading_tick = ticks_ms()
            
            return T, P, RH, G, A, Td, G_index, iaq
        
        else:
            return
        
    
    def read_calibration(self):
        calibration_coefficients_1 = self.multibyte_read(BME680_COEFF_START_ADDR_1, 25)
        calibration_coefficients_2 = self.multibyte_read(BME680_COEFF_START_ADDR_2, 16)
        
        self.cal_T1 = float(self.make_word(calibration_coefficients_2[9], calibration_coefficients_2[8]))
        self.cal_T2 = float(self.make_signed_word(self.make_word(calibration_coefficients_1[2], calibration_coefficients_1[1])))
        self.cal_T3 = float(self.make_signed_byte(calibration_coefficients_1[3]))
        
        self.cal_P1 = float(self.make_word(calibration_coefficients_1[6], calibration_coefficients_1[5]))
        self.cal_P2 = float(self.make_signed_word(self.make_word(calibration_coefficients_1[8], calibration_coefficients_1[7])))
        self.cal_P3 = float(self.make_signed_byte(calibration_coefficients_1[9]))    
        self.cal_P4 = float(self.make_signed_word(self.make_word(calibration_coefficients_1[12], calibration_coefficients_1[11])))
        self.cal_P5 = float(self.make_signed_word(self.make_word(calibration_coefficients_1[14], calibration_coefficients_1[13])))
        self.cal_P6 = float(self.make_signed_byte(calibration_coefficients_1[16]))
        self.cal_P7 = float(self.make_signed_byte(calibration_coefficients_1[15]))
        self.cal_P8 = float(self.make_signed_word(self.make_word(calibration_coefficients_1[20], calibration_coefficients_1[19])))
        self.cal_P9 = float(self.make_signed_word(self.make_word(calibration_coefficients_1[22], calibration_coefficients_1[21])))
        self.cal_P10 = float(calibration_coefficients_1[23])
        
        self.cal_RH1 = float(((calibration_coefficients_2[2] << 4) | (calibration_coefficients_2[1] >> 4) & 0x0F))
        self.cal_RH2 = float(((calibration_coefficients_2[0] << 4) | (calibration_coefficients_2[1] >> 4) & 0x0F))
        self.cal_RH3 = float(self.make_signed_byte(calibration_coefficients_2[3]))
        self.cal_RH4 = float(self.make_signed_byte(calibration_coefficients_2[4]))
        self.cal_RH5 = float(self.make_signed_byte(calibration_coefficients_2[5]))
        self.cal_RH6 = float(calibration_coefficients_2[6])
        self.cal_RH7 = float(self.make_signed_byte(calibration_coefficients_2[7]))
        
        self.cal_G1 = float(self.make_signed_byte(calibration_coefficients_2[12]))
        self.cal_G2 = float(self.make_signed_word(self.make_word(calibration_coefficients_2[11], calibration_coefficients_2[10])))
        self.cal_G3 = float(self.make_signed_byte(calibration_coefficients_2[13]))
        
        self.heat_val = float(self.multibyte_read(BME680_RES_HEAT_VAL_ADDR, 1)[0])
        self.heat_range = float(((self.multibyte_read(BME680_RES_HEAT_RANGE_ADDR, 1)[0]) & 0x30) / 16)
        self.sw_err = float(((self.multibyte_read(BME680_RANGE_SW_ERR_ADDR, 1)[0]) & 0xF0) / 16)
        