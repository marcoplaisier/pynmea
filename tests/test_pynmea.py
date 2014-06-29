# -*- coding: utf-8 -*-

"""
test_pynmea
----------------------------------

Tests for `pynmea` module.
"""

import unittest
from pynmea.pynmea import NMEA


class TestExamples(unittest.TestCase):
    def setUp(self):
        pass

    def test_example(self):
        expected = '$GPRMC,161229.487,A,3723.2475,N,12158.3416,W,0.13,309.62,120598,,*10\r\n'
        parameters = {'time': 161229.487,
                      'warning': 'A',
                      'latitude': 3723.2475,
                      'latitude_indicator': 'N',
                      'longitude': 12158.3416,
                      'longitude_indicator': 'W',
                      'speed': 0.13,
                      'course_over_ground': 309.62,
                      'date': 120598,
                      'magnetic_variation': ''}
        result = str(NMEA(parameters))
        self.assertEqual(result, expected)

    def test_example_2(self):
        expected = '$GPRMC,155123.0,A,4043.8432,N,07359.7653,W,0.15,83.25,200407,,*28\r\n'
        parameters = {'time': '155123.000',
                      'warning': 'A',
                      'latitude': 4043.8432,
                      'latitude_indicator': 'N',
                      'longitude': '07359.7653',
                      'longitude_indicator': 'W',
                      'speed': 0.15,
                      'course_over_ground': 83.25,
                      'date': 200407,
                      'magnetic_variation': '',}
        result = str(NMEA(parameters))
        self.assertEqual(result, expected)

    def test_checksum(self):
        expected = str(hex(ord('a') ^ ord('b'))).replace('0x','')
        nmea = NMEA({})
        result = nmea.calculate_checksum('ab')
        self.assertEqual(expected, result)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()