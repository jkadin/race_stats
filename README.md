# race_stats
Download and parse subsession data from iRacing to get lap times


usage: race_stats.py [-h] -u USER -p PASSWORD -s SUBSESSION_ID -o OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  iRacing username
  -p PASSWORD, --password PASSWORD
                        iRacing password
  -s SUBSESSION_ID, --subsession_id SUBSESSION_ID
                        Subsession ID
  -o OUTPUT, --output OUTPUT
                        Full path to write the csv file to. Make sure to use
                        quotes if the path contains spaces.
