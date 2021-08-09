from dgp import dgp as test_func
import argparse
import time
import datetime
import pandas as pd
import os
from statistics import mean
from tabulate import tabulate
try:
    import adc
except:
    print("Error importing ADC script. Perhaps this program is not being called on an rPi with ADCPi installed?")
    print("Attempting to run without import (only works with --testing flag).")

def main(args):
    # Start the timer
    t0 = time.time()

    # Collect Arguments
    stop_time = time.time() + args.time if args.time else time.time() + 300
    file_name = args.filename if args.filename else datetime.datetime.now().strftime("%m-%d-%Y_%H:%M")
    interval = args.interval if args.interval else 5
    interval_time = time.time() + interval
    mph = args.mph
    unit = 'MPH' if mph else 'm/s'

    # Initialize Data Structures
    data = {
        'time': [],
        'value': []
    }
    ma_V = []
    ma_w = [0]
    func = test_func if args.testing else adc.read


    cnt = 0
    vals = []
    for value in func():
        # Stabilize Voltage Reading
        if cnt < 20:
            cnt += 1
            vals.append(voltage2velocity(value,mph))
            continue
        offset = mean(vals)

        t = time.time()
        # Check Stopping Criteria
        if time.time() > stop_time:
            break

        # Collect Data
        value = voltage2velocity(value,mph)
        value = value - offset
        data['time'].append(t)
        data['value'].append(value)

        # Output Data to Console
        ma_V.append(value)
        if len(ma_V) > 5:
            ma_V.pop(0)
            os.system("clear")
            print("*** Collecting Airspeed Data ***\n")
            out = [
                ['Elapsed', round(time.time()-t0,0), 's'],
                ['Remaining', round(stop_time-time.time(), 0), 's'],
                ['Velocity', round(mean(ma_V), 4), unit],
                ['Write time', round(mean(ma_w), 4), 's']
            ]
            print(tabulate(out,headers=('Quantity', 'Value', 'Units')))

        # Write Data (if interval)
        if time.time() > interval_time:
            t = writedata(data, file_name)

            # Save output time
            ma_w.append(t)
            if len(ma_w) > 5:
                ma_w.pop(0)

            # Reset write interval time
            interval_time = time.time() + interval

    # Write Data
    writedata(data, file_name)

    print("\n*** Ending Data Collection ***")
    print("Program ran for {0} seconds.".format(args.time))


def writedata(data, filename):
    df = pd.DataFrame.from_dict(data)
    df.set_index("time", inplace=True)

    t1 = time.time()
    df.to_csv('data/{0}.csv'.format(filename))
    os.system("sync")
    t2 = time.time()

    return round(t2 - t1, 4)


def voltage2velocity(value,mph):
    # Perform Voltage to Velocity Calculation
    velocity = ((2000/1.2)*abs(5*(value/3.3)-3.3/2))**0.5

    if mph:
        velocity *= 2.23694

    return velocity


if __name__ == "__main__":
    # Parse CLI Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename",
                        help="Filename to use for output (no extension, string)",
                        type=str)
    parser.add_argument("-t", "--time",
                        help="Time to collect data for (seconds, integer). Defaults to 5 minutes.",
                        type=int)
    parser.add_argument("--interval",
                        help="Time interval to write data to disk (seconds, integer). Defaults to 5 seconds.",
                        type=int)
    parser.add_argument("--testing",
                        help="Testing mode. Uses random.uniform() as a data generating process instead of reading ADC pin voltage",
                        action="store_true")
    parser.add_argument("--mph",
                        help="Converts velocity values to MPH",
                        action="store_true")
    args = parser.parse_args()

    main(args)
