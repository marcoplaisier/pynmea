# -*- coding: utf-8 -*-

"""
test_pynmea
----------------------------------

Tests for `pynmea` module.
"""

import unittest
from mock import patch
from pynmea.pynmea import NMEA


@patch('pynmea.pynmea.NMEA.load_library')
class TestExamples(unittest.TestCase):
    def setUp(self):
        pass

    def test_example(self, mock_class):
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
        self.assertEqual(mock_class.call_count, 1)
        self.assertEqual(result, expected)

    def test_example_2(self, mock_class):
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
        self.assertEqual(mock_class.call_count, 1)
        self.assertEqual(result, expected)

    def test_checksum(self, mock_class):
        expected = str(hex(ord('a') ^ ord('b'))).replace('0x','')
        nmea = NMEA({})
        result = nmea.calculate_checksum('ab')
        self.assertEqual(mock_class.call_count, 1)
        self.assertEqual(expected, result)

    def test_string_generator(self, mock_class):
        expected1 = '$GPRMC,155123.0,A,,,,,,,200407,,*38\r\n'
        expected2 = '$GPRMC,155124.0,A,,,,,,,200407,,*3f\r\n'
        nmea = NMEA({
            'warning': 'A',
            'time': 155123.0,
            'date': 200407
        })
        gen = nmea.get_nmea_string()
        result1 = gen.send(None)
        self.assertEqual(mock_class.call_count, 1)
        self.assertEqual(result1, expected1)

        timestamp = nmea.get_timestamp()
        result2 = gen.send(timestamp.replace(seconds=+1))
        self.assertEqual(mock_class.call_count, 1)
        self.assertEqual(result2, expected2)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()