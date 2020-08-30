import os
import csv
import asyncio
import argparse
from pyracing.constants import SimSessionType
from pyracing.client import Client


def time_convert(lap_time):
    millis = int(lap_time/10)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24
    return ("%02d:%02d.%03d" % (minutes, seconds, millis%1000))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="iRacing username", required=True)
    parser.add_argument("-p", "--password", help="iRacing password", required=True)
    parser.add_argument("-s", "--subsession_id", help="Subsession ID", required=True)
    parser.add_argument("-o", "--output", help="Full path to write the csv file to. Make sure to use quotes if the path contains spaces.", required=True)

    args = parser.parse_args()

    ir = Client(args.user, args.password)
    subsession_data = await ir.race_laps_all(subsession_id=args.subsession_id, sim_session_type=SimSessionType.race.value)
    drivers = subsession_data.driver
    drivers = dict([(d.cust_id, d.display_name.replace('+', ' ')) for d in drivers])
    race_laps = subsession_data.lap_data
    data = {}
    for lap in race_laps:
        driver_name = drivers[lap.cust_id]
        if not driver_name in data:
            data[driver_name] = []
        data[driver_name].append([lap.car_num, lap.lap_num, lap.time_ses])
    csv_file = args.output
    with open(csv_file, 'w') as f:
        csvw = csv.writer(f)
        for driver, laps in sorted(data.items()):
            laps = sorted(laps, key = lambda x: x[1])
            for i, lap in enumerate(laps):
                if i == 0:
                    lap_time = 0
                else:
                    lap_time = lap[2] - laps[i-1][2]
                lap_time = time_convert(lap_time)
                csvw.writerow([driver, lap[0], lap[1], lap_time])
    print("Data written to : %s" % csv_file)


asyncio.run(main())
