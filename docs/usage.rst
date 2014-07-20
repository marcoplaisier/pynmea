Usage
========

To use PyNMEA in a project::

	import pynmea

You probably want to use PyNMEA as a stand-alone application though. In that case, you might want to check out the
configuration file ``example.ini``. Then run::

    python pynmea.py

If you want to use another configuration file, then::

	python pynmea.py —file filename.ini

Configuration
-
Below is the example configuration included with pynmea. All options must be present, but you can leave them empty. 
   
	[GPS]
	course = 0
	magnetic_variation = 0
	magnetic_variation_indicator = E
	longitude = 0528.4080
	longitude_indicator = E
	latitude_indicator = N
	latitude = 5126.1174
	warning = A
	speed = 0

	[START]
	start-date = 290614
	start-time = 120000.000

	[STEP]
	step-size = 1
	# choose one from: 
	# year, month, day, hour, minute, second, microsecond
	quantity = hour

Output
-

The important bit is the output. Most GPS devices send the string through a serial port at 4800 bytes. PyNMEA uses the serial port on port GPIO 14 (UART0_TXD) and GPIO 15 (UART0_RXD) to do the same. 