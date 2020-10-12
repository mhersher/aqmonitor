from sds011 import SDS011
import time

class SDS011():
    def __init__(self,device_path = '/dev/serial0',baud_rate = 9600,pin_sleep):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_sleep, GPIO.OUT)
        GPIO.output(pin_sleep, GPIO.HIGH)
        self.gpio = GPIO
        self.status = 1
        self.device = pm_sensor=SDS011(pm_sensor_path, use_query_mode=True)

    def enable(self):
        print('enabling')
        if self.status == 0:
            self.device.sleep(sleep=False)
            time.sleep(30)
        self.status = 1
        return status

    def disable(self):
        print('disabling')
        self.device.sleep(sleep=True)
        self.status = 0
        return status

    def read(self):
        print('reading')
        enable(self)
        data = pms5003.read()
        print(data)
        disable(self)
        return data
