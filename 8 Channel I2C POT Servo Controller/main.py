from array import array
from micropython import const
from machine import I2C, PWM, Pin
from time import sleep_ms
from I2C_POT import I2C_POT


POT_MIN = const(0)
POT_MAX = const(4095)

SERVO_PIN_START = const(14)
NO_OF_SERVOS = const(8)
SERVO_PWM_FREQUENCY = const(50)

SERVO_0 = const(3000)
SERVO_90 = const(4915)
SERVO_180 = const(7000)

SERVO_ANGLE_MIN = const(0)
SERVO_ANGLE_MAX = const(180)

SAMPLING_TIME = const(10)


i = 0
pwm = 0
pos = array('H', [0, 0, 0, 0, 0, 0, 0, 0])
servo = array('H', [0, 0, 0, 0, 0, 0, 0, 0])

servo = [None] * 8

LED = Pin(25, Pin.OUT)

i2c = I2C(0, scl = Pin(5), sda = Pin(4), freq = 100000)  

pot = I2C_POT(i2c)


for i in range(0, NO_OF_SERVOS):
    servo[i] = PWM(Pin(SERVO_PIN_START + i))
    servo[i].freq(SERVO_PWM_FREQUENCY)
    servo[i].duty_u16(SERVO_90)

sleep_ms(3000)


def map_value(v, x_min, x_max, y_min, y_max):
    value = int(y_min + (((y_max - y_min) / (x_max - x_min)) * (v - x_min)))
    value = constrain_value(value, y_max, y_min)
    return value


def constrain_value(v, max_v, min_v):
    if(v >= max_v):
        v = max_v
    
    if(v <= min_v):
        v = min_v
        
    return v


def set_servo_pos(channel, value):
    position = map_value(value, POT_MIN, POT_MAX, SERVO_0, SERVO_180)
    angle = map_value(position, SERVO_0, SERVO_180, SERVO_ANGLE_MIN, SERVO_ANGLE_MAX)
    servo[channel].duty_u16(position)
    print("CH " + str(channel) + ":  " + str(angle))
    
    
def set_all_servos():
    global pos
    pos = pot.read_all_channel_avg()
    for i in range(0, NO_OF_SERVOS):
        set_servo_pos(i, pos[i])
    print("\r\n")


while(True):
    LED.toggle()
    set_all_servos()
    sleep_ms(SAMPLING_TIME)

