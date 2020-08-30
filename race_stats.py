import os
import csv
import asyncio
import argparse
from pyracing.constants import SimSessionType
from pyracing.client import Client


def time_convert(lap_time):
    # For some reason lap_time (time_ses) is in milliseconds * 10
    millis = int(lap_time/10)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24
    return ("%02d:%02d.%03d" % (minutes, seconds, millis%1000))


async def main():
    # Get command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="iRacing username", required=True)
    parser.add_argument("-p", "--password", help="iRacing password", required=True)
    parser.add_argument("-s", "--subsession_id", help="Subsession ID", required=True)
    parser.add_argument("-o", "--output", help="Full path to write the csv file to. Make sure to use quotes if the path contains spaces.", required=True)

    args = parser.parse_args()

    # Download data from iRacing
    ir = Client(args.user, args.password)
    subsession_data = await ir.race_laps_all(subsession_id=args.subsession_id, sim_session_type=SimSessionType.race.value)
    drivers = subsession_data.driver
    drivers = dict([(d.cust_id, d.display_name.replace('+', ' ')) for d in drivers])
    race_laps = subsession_data.lap_data

    # Group and sort data by driver
    data = {}
    max_lap_num = 0
    for lap in race_laps:
        driver_name = "%s - #%s" % (drivers[lap.cust_id], lap.car_num)
        if not driver_name in data:
            data[driver_name] = []
        data[driver_name].append([lap.lap_num, lap.time_ses])
        if lap.lap_num > max_lap_num:
            max_lap_num = lap.lap_num

    # Convert time_ses to lap time
    converted_data = {}
    for driver, laps in data.items():
        converted_data[driver] = []
        laps = sorted(laps, key = lambda x: x[0])
        for i in range(0, max_lap_num + 1):
            try:
                lap = laps[i]
                if i == 0:
                    lap_time = 0
                else:
                    lap_time = lap[1] - laps[i-1][1]
            except IndexError:
                lap_time = 0
            converted_data[driver].append(lap_time)

    # Convert to list of lists and pivot so drivers are row headers
    ordered_data = []
    for driver, laps in sorted(converted_data.items()):
        driver_list = [driver]
        driver_list.extend([time_convert(l) for l in laps[1:]])
        ordered_data.append(driver_list)
    ordered_data = zip(*ordered_data)

    # Output to CSV
    csv_file = args.output
    with open(csv_file, 'w') as f:
        csvw = csv.writer(f)
        csvw.writerows(ordered_data)

    print("Data written to : %s" % csv_file)


asyncio.run(main())
