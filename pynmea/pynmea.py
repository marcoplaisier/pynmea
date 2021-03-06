# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from ctypes import cdll, c_ubyte, util
import argparse
import time

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import arrow

TTY = '/dev/ttyAMA0'
SLEEP_TIME = 1
DEFAULT_STEP_SIZE = 0
BAUD_RATE = 2400


class NMEA(object):
    def __init__(self, params):
        self.protocol = 'GPRMC'
        self.warning = params.get('warning', 'V')
        self.latitude = params.get('latitude', '')
        self.latitude_indicator = params.get('latitude_indicator', '')
        self.longitude = params.get('longitude', '')
        self.longitude_indicator = params.get('longitude_indicator', '')
        self.speed = params.get('speed', '')
        self.course = params.get('course_over_ground', '')
        time = str(params.get('time', ''))
        date = str(params.get('date', ''))
        self._timestamp = self.timestamp(date, time)
        self.magnetic_variation = params.get('magnetic_variation', '')
        self.magnetic_variation_indicator = params.get('magnetic_variation_indicator', '')
        self.period = params.get('period', None)
        self.stepsize = int(params.get('step-size', DEFAULT_STEP_SIZE))
        self.handle = None
        self.fd = -1
        self.load_library()

    @staticmethod
    def timestamp(date, time):
        if time and '.' in time:
            t = arrow.get(time, 'HHmmss.SSS')
        elif time:
            t = arrow.get(time, 'HHmmss')
        else:
            t = arrow.now()

        if date:
            d = arrow.get(date, 'DDMMYY')
        else:
            d = arrow.now()

        timestamp = arrow.Arrow(
            year=d.year,
            month=d.month,
            day=d.day,
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            microsecond=t.microsecond
        )

        return timestamp

    def __str__(self):
        template = str('{self.protocol},'
                              '{self._timestamp:HHmmss.SSS},'
                              '{self.warning},'
                              '{self.latitude},'
                              '{self.latitude_indicator},'
                              '{self.longitude},'
                              '{self.longitude_indicator},'
                              '{self.speed},'
                              '{self.course},'
                              '{self._timestamp:DDMMYY},'
                              '{self.magnetic_variation},'
                              '{self.magnetic_variation_indicator}')

        filled_template = template.format(self=self)

        return '$' + filled_template + '*' + self.calculate_checksum(filled_template) + '\r\n'

    def get_nmea_string(self):
        while True:
            timestamp = yield str(self)
            time.sleep(SLEEP_TIME)

            if timestamp is not None:
                self._timestamp = timestamp

            if self.period == 'year':
                self._timestamp = self._timestamp.replace(years=+self.stepsize)
            elif self.period == 'month':
                self._timestamp = self._timestamp.replace(months=+self.stepsize)
            elif self.period == 'day':
                self._timestamp = self._timestamp.replace(days=+self.stepsize)
            elif self.period == 'hour':
                self._timestamp = self._timestamp.replace(hours=+self.stepsize)
            elif self.period == 'minute':
                self._timestamp = self._timestamp.replace(minutes=+self.stepsize)
            elif self.period == 'second':
                self._timestamp = self._timestamp.replace(seconds=+self.stepsize)
            elif self.period == 'microsecond':
                self._timestamp = self._timestamp.replace(microseconds=+self.stepsize)

    def get_timestamp(self):
        return self._timestamp

    @staticmethod
    def calculate_checksum(text):
        checksum = 0
        for character in text:
            checksum ^= ord(character)

        return str(hex(checksum)).replace('0x', '')

    def load_library(self):
        lib_name = util.find_library('wiringPi')
        print('Lib name: {}'.format(lib_name))
        self.handle = cdll.LoadLibrary(lib_name)
        print('Handle: {}'.format(self.handle))
        self.fd = self.handle.serialOpen(TTY, BAUD_RATE)
        print('Open serial interface: {}'.format(self.fd))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PNMEA creates NMEA GPS strings or parses them")
    parser.add_argument("--file", help="Read settings from a configuration file", default='example.ini')

    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.file)

    params = {'warning': config.get('GPS', 'warning'),
              'latitude': config.get('GPS', 'latitude'),
              'latitude_indicator': config.get('GPS', 'latitude_indicator'),
              'longitude': config.get('GPS', 'longitude'),
              'longitude_indicator': config.get('GPS', 'longitude_indicator'),
              'speed': config.get('GPS', 'speed'),
              'course': config.get('GPS', 'course'),
              'magnetic_variation': config.get('GPS', 'magnetic_variation'),
              'magnetic_variation_indicator': config.get('GPS', 'magnetic_variation_indicator'),
              'period': config.get('STEP', 'quantity'),
              'step-size': config.get('STEP', 'step-size'),
              'time': config.get('START', 'start-time'),
              'date': config.get('START', 'start-date')}

    pynmea = NMEA(params)
    gen = pynmea.get_nmea_string()
    pynmea_string = gen.send(None)
    while True:
        print(pynmea_string)
        b_array = bytearray(pynmea_string, 'ascii')
        data_list = c_ubyte * len(b_array)
        data = data_list(*b_array)
        result = pynmea.handle.serialPuts(pynmea.fd, data)
        print('Result: {}'.format(result))
        pynmea_string = gen.send(None)