import from serial import Serial
import time
from Adafruit_IO import Client
import aqi
from statistics import median
from sds011 import SDS011
import requests
from datetime import datetime, timedelta
import configparser
import argparse
import random

class aqreporter(object):
    def __init__(self):
        self.read_arguments()
        self.read_config_file()
        self.auth0_auth()
        print('init complete')

    def read_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
                "-c","--config-file",
                dest='config_file',
                help='config file',
                required=True
                )
        parser.add_argument(
                "-d","--debug",
                default=False,
                action='store_true',
                help='run in debug mode with shorter timers'
                )
        parser.add_argument(
                "-f","--fake-data",
                default=False,
                action='store_true',
                help='dont initialize or read sensors - instead send dummy data.'
                )
        args=parser.parse_args()
        if args.debug:
            self.debug=True
        else:
            self.debug=False
        if args.fake_data:
            self.dummy_data=True
        else:
            self.dummy_data=False
        self.configfile=args.config_file

    def read_config_file(self):
        config=configparser.ConfigParser()
        config.read(self.configfile)
        settings = config['DEFAULT']

        #Auth0 Auth Settings
        self.auth0_request_url = settings.get('auth0_request_url')
        self.auth0_grant_type = settings.get('auth0_grant_type')
        self.auth0_client_id = settings.get('auth0_client_id')
        self.auth0_client_secret = settings.get('auth0_client_secret')
        self.auth0_audience = settings.get('auth0_audience')

        #Device Master Settings
        self.device_id=settings.get('device_id')
        self.measurement_frequency=settings.get('measurement_frequency')
        if self.debug == True:
            self.measurement_frequency = 30
            self.measurement_delay = 2
        if self.dummy_data == False:
            pm_sensor_path=settings.get('pm_sensor_device')
            self.pm_sensor=SDS011(pm_sensor_path, use_query_mode=True)
            temp_sensor_path=settings.get('temp_sensor_device')
            self.temp_sensor=None #Dummy pending temp sensor implementation
            baro_sensor_path=settings.get('baro_sensor_device')
            self.baro_sensor=None #Dummy pending baro sensor implementation
        else:
            self.pm_sensor=None
            self.temp_sensor=None
            self.baro_sensor=None

        #Upload endpoint settings
        self.measurement_endpoint=settings.get('measurement_endpoint')

    def auth0_auth(self):
        headers = {'content-type':"application/x-www-form-urlencoded"}
        content = {'grant_type':self.auth0_grant_type,'client_id':self.auth0_client_id,'client_secret':self.auth0_client_secret,'audience':self.auth0_audience}
        auth_response = requests.post(self.auth0_request_url,content,headers)
        if auth_response.ok == False:
            print(auth_response.status_code, auth_response.content)
            raise AuthError
        self.access_token = auth_response.json()['access_token']
        ttl = auth_response.json()['expires_in']
        self.expiry = datetime.now() + timedelta(seconds=ttl)
        self.token_type = auth_response.json()['token_type']

    def post_reading(self,reading):
        headers = {'content-type':'application/json','authorization':self.token_type+' '+self.access_token}
        post = requests.post(self.measurement_endpoint,json=reading,headers=headers)
        if post.ok == False:
            print(post.status_code, post.content)
            print(post.request.headers, post.request.body)
            raise PostError

    def read_pm_sensor(self):
        if self.dummy_data==True:
            pm=(random.randrange(0,400,1)/2,random.randrange(0,400,2)/4,random.randrange(0,250,5),random.randrange(0,250,5))
            return pm
        self.pm_sensor.sleep(sleep=False)
        pm25reads = []
        pm10reads = []
        time.sleep(self.measurement_delay)
        readcount=0
        while readcount<3:
            data=self.pm_sensor.query()
            pm25reads.append(data[0])
            pm10reads.append(data[1])
            time.sleep(2)
            readcount += 1
        self.pm_sensor.sleep()

        pm25raw=median(pm25reads)
        pm10raw=median(pm10reads)
        pm25aqi=aqi.to_iaqi(aqi.POLLUTANT_PM25,pm25raw,algo=aqi.ALGO_EPA)
        pm10aqi=aqi.to_iaqi(aqi.POLLUTANT_PM10,pm10raw,algo=aqi.ALGO_EPA)
        return (pm25raw, pm10raw, pm25aqi, pm10aqi)

    def read_temp_sensor(self):
        if self.dummy_data==True:
            temp=random.randrange(-40,80,1)/2
            return temp
        temp = None #dummy data for now
        return temp

    def read_baro_sensor(self):
        if self.dummy_data==True:
            baro=random.randrange(900,1200,1)
            return baro
        baro = None #dummy data in mbar
        return baro

    @staticmethod
    def assemble_reading(device_id, pm = None, temp = None, baro = None):
        reading={}
        formatted_measurement_time=datetime.utcnow().isoformat()+"Z"
        reading['measured_at']=formatted_measurement_time
        reading['pm10raw']=pm[1]
        reading['pm10aqi']=pm[3]
        reading['pm25raw']=pm[0]
        reading['pm25aqi']=pm[2]
        reading['temp']=temp
        reading['baro']=baro
        reading['device_id']=device_id
        return reading

    def poller(self):
        while True:
            print('Reading pm')
            pm=self.read_pm_sensor()

            print('Reading temp')
            temp=self.read_temp_sensor()

            print('Reading baro')
            baro=self.read_baro_sensor()

            print('Assembling reading')
            reading=self.assemble_reading(self.device_id,pm,temp,baro)
            if self.expiry <= datetime.now():
                self.auth0_auth()
            print('Sending reading')
            result=self.post_reading(reading)

            time.sleep(self.measurement_frequency-self.measurement_delay-4)

if __name__=="__main__":
    aqreporter().poller()
