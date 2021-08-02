#!/usr/bin/env python
"""
================================================
ABElectronics ADC Pi 8-Channel ADC demo *altered by Brandon Johnson*
Requires python smbus to be installed
================================================
Initialise the ADC device using the default addresses and sample rate,
change this value if you have changed the address selection jumpers
Sample rate can be 12,14, 16 or 18
"""

from __future__ import absolute_import, division, print_function, \
                                                    unicode_literals
import time

try:
    from ADCPi import ADCPi
except ImportError:
    print("Failed to import ADCPi from python system path")
    print("Importing from parent folder instead")
    try:
        import sys
        sys.path.append('..')
        from ADCPi import ADCPi
    except ImportError:
        raise ImportError(
            "Failed to import library from parent folder")


def read():
    '''
    Main program function
    '''

    adc = ADCPi(0x68, 0x69, 12)

    while True:

        # read from adc channel and yield to parent
        voltage = adc.read_voltage(1)
        yield voltage

        # wait 0.2 seconds before reading the pins again
        time.sleep(0.2)

if __name__ == "__main__":
    read()