import board
import busio
import adafruit_sht31d

class device():
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.device = adafruit_sht31d.SHT31D(i2c)
        self.status = 1

    def enable(self):
        #Implement enable and disable just for consistency across meters
        return 1

    def disable(self):
        return 1

    def read(self):
        standardized_data = {'temp':self.device.temperature,'humidity':self.device.relative_humidity}
        return standardized_data
