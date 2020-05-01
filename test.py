import serial, time
from Adafruit_IO import Client
import aqi

adafruit_client = Client('mhersher','aio_hTlE44GzdxxdsN8Eda4RHz5SNCE4')

device=serial.Serial('/dev/ttyUSB0')

def read_sensor():
    data = []
    #Read Raw Data from Sensor
    for index in range (0,10):
        datum = device.read()
        data.append(datum)
    return(data)

def calculate_values(data):
    results=[]
    #Extract raw values from serial output
    pmtwofive = int.from_bytes(b''.join(data[2:4]), byteorder='little')/10
    pmten = int.from_bytes(b''.join(data[4:6]), byteorder='little')/10
    results.append((['pmtwofive-indoor',pmtwofive]))
    results.append((['pmten-indoor',pmten]))
    print('PM 2.5: ',pmtwofive)
    print('PM 10: ',pmten)
    
    #Convert to AQI
    pmtwofiveaqi = int(aqi.to_iaqi(aqi.POLLUTANT_PM25, pmtwofive))
    pmtenaqi = int(aqi.to_iaqi(aqi.POLLUTANT_PM10, pmten))
    results.append((['pmtwofive-indoor-aqi',pmtwofiveaqi]))
    results.append((['pmten-indoor-aqi',pmtenaqi]))

    return results

def send_data(stream,point):
    try:
        adafruit_client.send(stream,point)
    except RequestError as error:
        print('Error sending '+result[0])
        print(err)

def to_aqi(pollutant,point):
    aqi=point.to_iaqi(pollutant,point,algo=aqi.ALGO_EPA)
    return aqi

def poller():
    while True:
        print('Reading sensor')
        data = read_sensor()

        print('Calculating values')
        results = calculate_values(data)

        print('Sending Data')
        for result in results:
            send_data(result[0],result[1])

        time.sleep(10)

if __name__=="__main__":
    poller()
