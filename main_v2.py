import json
import requests
import pickle
import os
import datetime
import logging
import pandas as pd

# make flask logging readable!
# TODO make better :D
log = logging.getLogger("uba-grabber-v2")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_logging_handler = logging.StreamHandler()
console_logging_handler.setFormatter(formatter)
log.addHandler(console_logging_handler)
log.setLevel(logging.DEBUG)


from things.station import Station
from things.airquality_data import AirqualityData



URLs = []

def get_stations(start, end, bundesland_filter=None):
    log.info("getting stations")
    if not os.path.isfile('station_request_%s-%s.pickle' % (start, end)):
        log.debug("no cached stations, downloading - may take a while")
        r = requests.get('https://www.umweltbundesamt.de/api/air_data/v2/stations/json?use=airquality&lang=de&date_from='+ start + '&time_from=1&date_to=' + end + '&time_to=24')
        with open('station_request_%s-%s.pickle' % (start, end), 'wb') as handle:
            pickle.dump(r, handle)
    with open('station_request_%s-%s.pickle' % (start, end), 'rb') as handle:
        r = pickle.load(handle)

    # create stations
    station_request = r.json()
    all_stations = []
    for key,value in station_request['data'].items():
        all_stations.append(Station(value, station_request['indices']))

    if bundesland_filter:
        filtered_stations = [] 
        for station in all_stations:
            if station.network_code == bundesland_filter:
                filtered_stations.append(station)
        return filtered_stations
    else:
        return all_stations

def get_station_data(station_id, start, end):
    log.info("get data of station %s", station_id)
    filename = '%s-data-request-%s-%s.pickle' % (station_id, start, end)
    if not os.path.isfile(filename):
        log.debug("no cached data for station: %s, downloading", station_id)
        url = 'https://www.umweltbundesamt.de/api/air_data/v2/airquality/json?date_from='+ start + '&time_from=1&date_to=' + end + '&time_to=24&station='+ station_id + '&lang=de'
        URLs.append(url)
        r = requests.get(url)
        with open(filename, 'wb') as handle:
            pickle.dump(r, handle)

    with open(filename, 'rb') as handle:
        r = pickle.load(handle)

    request = r.json()
    
    airquality_data = AirqualityData(station_id, request["data"], request["indices"]["data"])

    return airquality_data

def get_station_with_data():
    filename = 'stations_with_data.pickle'
    if not os.path.isfile(filename):
        ## predefines
        START = '2019-01-01'
        END = '2020-12-31'

        stations = get_stations(START, END, 'SH')
        for station in stations:
            station.data = get_station_data(station.station_id, START, END)

        with open(filename, 'wb') as handle:
            pickle.dump(stations, handle)
        return stations

    with open(filename, 'rb') as handle:
        stations = pickle.load(handle)
    return stations


def get_station_with_data_only_feinstaub():
    # get all feinstaub values
    filename = 'stations_data_only_feinstaub.pickle'
    if not os.path.isfile(filename):
        feinstaub_stations = [] 
        for station in get_station_with_data():
            feinstaub_measurements = []
            for measurement in station.data.measurements:
                for messung in measurement.messung:
                    if messung.component_id == 1:
                        measurement.messung = [messung]
                        feinstaub_measurements.append(measurement)
            if feinstaub_measurements.__len__() > 0:
                station.data.measurements = feinstaub_measurements
                feinstaub_stations.append(station)


        with open(filename, 'wb') as handle:
            pickle.dump(feinstaub_stations, handle)
        return feinstaub_stations

    with open(filename, 'rb') as handle:
        feinstaub_stations = pickle.load(handle)
    return feinstaub_stations

def get_ave_per_month(array):
    import numpy as np

    result = []
    for idx, month in enumerate(array):
        result.append(np.sum(array[idx])/array[idx].__len__())
    
    return result

stations = get_station_with_data_only_feinstaub()
for station in stations:
    station.monthly = []
    date, total_index, index, value, y_value = ([], [], [], [], [])
    for i in range(24):
        station.monthly.append([])
        date.append([])
        total_index.append([])
        index.append([])
        value.append([])
        y_value.append([])
    for measurement in station.data.measurements:
        month = measurement.date.month
        year = measurement.date.year
        if year ==2020:
            month+=12
        date[month-1].append(measurement.date)
        total_index[month-1].append(measurement.total_index)
        index[month-1].append(measurement.messung[0].index)
        value[month-1].append(measurement.messung[0].value)
        y_value[month-1].append(float(measurement.messung[0].y_value))
    d = {'total_index': get_ave_per_month(total_index), 'index': get_ave_per_month(index), 'value': get_ave_per_month(value), 'y_value': get_ave_per_month(y_value)}
    dataframe = pd.DataFrame(d)
    dataframe.to_excel("%s-monthly.xlsx" % station.station_code)  


 

    
    
print('end')