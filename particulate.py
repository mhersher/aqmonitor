import serial, time
from Adafruit_IO import Client
import aqi
from statistics import median
from sds011 import SDS011

adafruit_client = Client('mhersher','aio_hTlE44GzdxxdsN8Eda4RHz5SNCE4')

sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
measurement_frequency=300

#device=serial.Serial('/dev/ttyUSB0')

def read_sensor(delay=20):
    sensor.sleep(sleep=False)
    pm25reads = []
    pm10reads = []
    time.sleep(delay)
    readcount=0
    while readcount<3:
        data=sensor.query()
        pm25reads.append(data[0])
        pm10reads.append(data[1])
        time.sleep(2)
        readcount += 1
    pm25=median(pm25reads)
    pm10=median(pm10reads)
    data=(pm25, pm10)
    sensor.sleep()
    return data
def calculate_values(data):
    results = []
    #Convert to AQI
    pm25aqi = int(aqi.to_iaqi(aqi.POLLUTANT_PM25, data[0]))
    pm10aqi = int(aqi.to_iaqi(aqi.POLLUTANT_PM10, data[1]))
    results.append((['pmtwofive-indoor-aqi',pm25aqi]))
    results.append((['pmten-indoor-aqi',pm10aqi]))
    print(pm25aqi)
    print(pm10aqi)

    return results

def send_data(stream,point):
    try:
        adafruit_client.send(stream,point)
    except RequestError as error:
        print('Error sending '+result[0])
        print(err)

def to_aqi(pollutant,point):
    calculated_aqi=point.to_iaqi(pollutant,point,algo=aqi.ALGO_EPA)
    return calculated_aqi

def poller():
    while True:
        print('Reading sensor')
        data=read_sensor()

        print('Calculating values')
        results = calculate_values(data)

        print('Sending Data')
        for result in results:
            send_data(result[0],result[1])

        time.sleep(measurement_frequency-20)

if __name__=="__main__":
    poller()
