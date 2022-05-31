import os
import json
for root, dirs, files in os.walk('./cache', topdown=True):
    for file in files:
        dates = file.split('.')[0].split('_')
        start_date, end_date = dates[0], dates[1]
        print(start_date, end_date)