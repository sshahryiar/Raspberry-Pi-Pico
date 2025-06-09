from machine import I2C
from micropython import const 
from time import sleep_ms
import math

AK8975_DEFAULT_I2C_ADDRESS = const(0x0C)
AK8975_ID_REG = const(0x00)
AK8975_ST1_REG = const(0x02)
AK8975_HXL_REG = const(0x03)
AK8975_HXH_REG = const(0x04)
AK8975_HYL_REG = const(0x05)
AK8975_HYH_REG = const(0x06)
AK8975_HZL_REG = const(0x07)
AK8975_HZH_REG = const(0x08)
AK8975_ST2_REG = const(0x09)
AK8975_CNTL_REG = const(0x0A)
AK8975_ASTC_REG = const(0x0C)
AK8975_ASAX_REG = const(0x10)
AK8975_ASAY_REG = const(0x11)
AK8975_ASAZ_REG = const(0x12)

AK8975_CTRL_POWERDOWN_MODE = const(0x00)
AK8975_CTRL_SINGLE_MODE = const(0x01)
AK8975_CTRL_SELFTEST_MODE = const(0x08)
AK8975_CTRL_FUSE_ACCESS_MODE = const(0x0F)


class AK8975:
    def __init__(self, _i2c, _i2c_addr=AK8975_DEFAULT_I2C_ADDRESS):
        self.i2c = _i2c
        self.i2c_address = _i2c_addr
        self.asax = 0
        self.asay = 0
        self.asaz = 0

        # Hard iron offset
        self.calibration_offset_x_axis = 0
        self.calibration_offset_y_axis = 0
        self.calibration_offset_z_axis = 0

        # Soft iron scale
        self.calibration_scale_x_axis = 1.0
        self.calibration_scale_y_axis = 1.0
        self.calibration_scale_z_axis = 1.0

        self.soft_reset()

        if self.read_byte(AK8975_ID_REG) != 0x48:
            raise Exception("AK8975 not found!")

        else:
            self.self_test()
            self.get_sensitivity_adjustment_values()
            self.set_sensitivity_adjustment_values()


    def write_byte(self, reg, value):
        self.i2c.writeto_mem(self.i2c_address, reg, bytes([value]))


    def read_byte(self, reg):
        return self.read_multi_byte(reg, 1)[0]


    def read_multi_byte(self, reg, no_of_bytes):
        return self.i2c.readfrom_mem(self.i2c_address, reg, no_of_bytes)


    def set_mode(self, mode):
        if mode not in (AK8975_CTRL_POWERDOWN_MODE,
                        AK8975_CTRL_SINGLE_MODE,
                        AK8975_CTRL_SELFTEST_MODE,
                        AK8975_CTRL_FUSE_ACCESS_MODE):
            raise ValueError("Invalid mode")
        self.write_byte(AK8975_CNTL_REG, mode)
        sleep_ms(10)


    def self_test(self):
        self.set_mode(AK8975_CTRL_POWERDOWN_MODE)
        self.write_byte(AK8975_ASTC_REG, 0x40)
        self.set_mode(AK8975_CTRL_SELFTEST_MODE)
        raw = self.read_raw_magnetic_data()
        print("Self-test data:", raw)
        self.write_byte(AK8975_ASTC_REG, 0x00)
        self.set_mode(AK8975_CTRL_POWERDOWN_MODE)


    def soft_reset(self):
        self.set_mode(AK8975_CTRL_POWERDOWN_MODE)
        sleep_ms(10)
        self.set_mode(AK8975_CTRL_SELFTEST_MODE)
        sleep_ms(10)


    def get_sensitivity_adjustment_values(self):
        self.set_mode(AK8975_CTRL_FUSE_ACCESS_MODE)
        sleep_ms(10)
        self.asax = self.read_byte(AK8975_ASAX_REG)
        self.asay = self.read_byte(AK8975_ASAY_REG)
        self.asaz = self.read_byte(AK8975_ASAZ_REG)
        self.set_mode(AK8975_CTRL_POWERDOWN_MODE)


    def set_sensitivity_adjustment_values(self):
        self.set_mode(AK8975_CTRL_FUSE_ACCESS_MODE)
        sleep_ms(10)
        self.write_byte(AK8975_ASAX_REG, self.asax)
        self.write_byte(AK8975_ASAY_REG, self.asay)
        self.write_byte(AK8975_ASAZ_REG, self.asaz)
        self.set_mode(AK8975_CTRL_POWERDOWN_MODE)


    def read_raw_magnetic_data(self):
        self.set_mode(AK8975_CTRL_SINGLE_MODE)
        sleep_ms(10)

        while not (self.read_byte(AK8975_ST1_REG) & 0x01):
            sleep_ms(1)

        data = self.read_multi_byte(AK8975_HXL_REG, 6)

        if self.read_byte(AK8975_ST2_REG) & 0x08:
            raise RuntimeError("Magnetic sensor overflow!")

        x_axis = self.twos_complement(self.make_word(data[1], data[0]))
        y_axis = self.twos_complement(self.make_word(data[3], data[2]))
        z_axis = self.twos_complement(self.make_word(data[5], data[4]))

        return x_axis, y_axis, z_axis


    def read(self):
        raw = self.read_raw_magnetic_data()

        x = self.convert_to_uT(raw[0], self.asax)
        y = self.convert_to_uT(raw[1], self.asay)
        z = self.convert_to_uT(raw[2], self.asaz)

        # Apply calibration offsets and scaling
        x = (x - self.calibration_offset_x_axis) * self.calibration_scale_x_axis
        y = (y - self.calibration_offset_y_axis) * self.calibration_scale_y_axis
        z = (z - self.calibration_offset_z_axis) * self.calibration_scale_z_axis

        return x, y, z


    def heading(self, val1, val2):
        heading_rad = math.atan2(val1, val2)
        heading_deg = math.degrees(heading_rad)

        while(heading_deg < 0):
            heading_deg += 360
        while(heading_deg > 360):
            heading_deg -= 360;
            
        return heading_deg


    def calibrate(self, no_of_samples=256):
        print("Calibrating. Move the sensor in a figure-8 pattern.")
        max_x, max_y, max_z = -32768, -32768, -32768
        min_x, min_y, min_z = 32767, 32767, 32767

        for _ in range(no_of_samples):
            try:
                x, y, z = self.read_raw_magnetic_data()
                max_x = max(max_x, x)
                min_x = min(min_x, x)
                max_y = max(max_y, y)
                min_y = min(min_y, y)
                max_z = max(max_z, z)
                min_z = min(min_z, z)
                sleep_ms(20)
            except:
                continue

        self.calibration_offset_x_axis = (max_x + min_x) / 2
        self.calibration_offset_y_axis = (max_y + min_y) / 2
        self.calibration_offset_z_axis = (max_z + min_z) / 2

        range_x = (max_x - min_x) / 2
        range_y = (max_y - min_y) / 2
        range_z = (max_z - min_z) / 2
        avg_range = (range_x + range_y + range_z) / 3

        self.calibration_scale_x_axis = avg_range / range_x
        self.calibration_scale_y_axis = avg_range / range_y
        self.calibration_scale_z_axis = avg_range / range_z

        print("Offsets:", self.calibration_offset_x_axis,
              self.calibration_offset_y_axis, self.calibration_offset_z_axis)
        print("Scales:", self.calibration_scale_x_axis,
              self.calibration_scale_y_axis, self.calibration_scale_z_axis)
        print("Calibration complete.")


    @staticmethod
    def convert_to_uT(value, adjustment):
        return ((value * (adjustment + 128) / 256.0) * 0.15) if adjustment else value * 0.15


    @staticmethod
    def make_word(msb, lsb):
        return (msb << 8) | lsb


    @staticmethod
    def twos_complement(value):
        if value > 32767:
            value -= 65536
        return value
