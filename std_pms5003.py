from pms5003 import PMS5003
import time
import RPi.GPIO as GPIO

class device():
    def __init__(self,device_path = '/dev/serial0',baud_rate = 9600,pin_sleep = 17):
        print(device_path,baud_rate,pin_sleep)
        self.pin_sleep = int(pin_sleep)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_sleep, GPIO.OUT)
        GPIO.output(self.pin_sleep, GPIO.HIGH)
        self.gpio = GPIO
        self.status = 1
        self.device = PMS5003(
            device=device_path,
            baudrate=baud_rate
        )

    def enable(self):
        print('Enabling Sensor')
        if self.status == 0:
            GPIO.output(self.pin_sleep, GPIO.HIGH)
            time.sleep(30)
        self.status = 1
        return self.status

    def disable(self):
        print('Disabling Sensor')
        GPIO.output(self.pin_sleep, GPIO.LOW)
        self.status = 0
        return self.status

    def read(self):
        print('reading')
        #self.enable()
        data = self.device.read()
        standardized_data = {'pm1':data.pm_ug_per_m3(1),'pm2.5':data.pm_ug_per_m3(2.5),'pm10':data.pm_ug_per_m3(10)}
        #self.disable()
        return standardized_data
