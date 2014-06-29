# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import arrow


class NMEA(object):
    def __init__(self, params):
        self.protocol = 'GPRMC'

        self.time = str(params.get('time', ''))
        if '.' not in self.time and self.time != '':
            time = arrow.get(self.time, 'HHmmss')
        elif self.time != '':
            time = arrow.get(self.time, 'HHmmss.SSS')
        else:
            time = None

        self.warning = params.get('warning', 'V')
        self.latitude = params.get('latitude', '')
        self.latitude_indicator = params.get('latitude_indicator', '')
        self.longitude = params.get('longitude', '')
        self.longitude_indicator = params.get('longitude_indicator', '')
        self.speed = params.get('speed', '')
        self.course = params.get('course_over_ground', '')

        self.date = str(params.get('date', ''))
        if self.date != '':
            date = arrow.get(self.date, 'DDMMYY')
        else:
            date = None

        if date is not None and time is not None:
            self._timestamp = date.replace(hour=time.hour, minute=time.minute, second=time.second,
                                           microsecond=time.microsecond)
        else:
            self._timestamp = None

        self.magnetic_variation = params.get('magnetic_variation', '')
        self.magnetic_variation_indicator = params.get('magnetic_variation_indicator', '')

    def __str__(self):
        if self._timestamp is not None:
            s = ('{self.protocol},'
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
        else:
            s = ('{self.protocol},'
                 '{self.time},'
                 '{self.warning},'
                 '{self.latitude},'
                 '{self.latitude_indicator},'
                 '{self.longitude},'
                 '{self.longitude_indicator},'
                 '{self.speed},'
                 '{self.course},'
                 '{self.date},'
                 '{self.magnetic_variation},'
                 '{self.magnetic_variation_indicator}')

        s = s.format(self=self)

        return '$' + s + '*' + self.calculate_checksum(s) + '\r\n'

    def get_nmea_strings(self):
        while True:
            self._timestamp = yield str(self)
            if self._timestamp is not None:
                self.date = self._timestamp.format('DDMMYY')
                print(self.time)
                self.time = self._timestamp.format('HHmmss.SSS')
                print(self.time)

    def get_timestamp(self):
        return self._timestamp

    @staticmethod
    def calculate_checksum(s):
        checksum = 0
        for c in s:
            checksum ^= ord(c)

        return str(hex(checksum)).replace('0x', '')

if __name__ == '__main__':
    pass