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
        self.stepsize = int(params.get('step-size', None))
        self.load_library()

    @staticmethod
    def timestamp(date, time):
        if time and '.' in time:
            t = arrow.get(time, 'HHmmss.SSS')
        elif time:
            t = arrow.get(time, 'HHmmss')
        else:
            t = None

        if date:
            d = arrow.get(date, 'DDMMYY')
        else:
            d = None

        if not (d or t):
            timestamp = None
        elif d and t:
            timestamp = arrow.get(year=d.year,
                                  month=d.month,
                                  day=d.day,
                                  hour=t.hour,
                                  minute=t.minute,
                                  second=t.second,
                                  microsecond=t.microsecond)
        elif not d:
            timestamp = date.replace()
        elif not t:
            timestamp = time.replace()
        return timestamp

    def __str__(self):
        s = str('{self.protocol},'
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

        s = s.format(self=self)

        return '$' + s + '*' + self.calculate_checksum(s) + '\r\n'

    def get_nmea_string(self):
        while True:
            timestamp = yield str(self)
            time.sleep(1)

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
    def calculate_checksum(s):
        checksum = 0
        for c in s:
            checksum ^= ord(c)

        return str(hex(checksum)).replace('0x', '')

    def load_library(self):
        lib_name = util.find_library('wiringPi')
        self.handle = cdll.LoadLibrary(lib_name)
        self.handle.serialOpen(0, 4800)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PNMEA creates NMEA GPS strings or parses them")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", help="Read settings from a configuration file")

    subgroup = group.add_argument_group()
    subgroup.add_argument("--starttime",
                          help="Set the start time and date used in the NMEA string (eg. 2014-03-06 11:15:01.125)",
                          default='2014-01-01 00:00:00.000')
    subgroup.add_argument("--stepsize",
                          help="Set the size of period to increase. Eg. 5",
                          type=int,
                          default=1)
    subgroup.add_argument("--period",
                          help="Set the period to increase. Eg. year",
                          default='second')
    args = parser.parse_args()
    if args.file:
        config = configparser.ConfigParser()
        config.read(args.file)
    else:
        config = configparser.ConfigParser()
        config.read('example.ini')

    params = {'warning': config.get('GPS', 'warning'),
              'latitude': config.get('GPS', 'latitude'),
              'latitude_indicator': config.get('GPS', 'latitude_indicator'),
              'longitude': config.get('GPS', 'longitude'),
              'longitude_indicator':config.get('GPS', 'longitude_indicator'),
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
    s = gen.send(None)
    for i in range(0, 10):
        print(s)
        b = bytearray(s)
        data_list = c_ubyte * len(b)
        data = data_list(*b)
        pynmea.handle.serialPuts(data)
        s = gen.send(None)