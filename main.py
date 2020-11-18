import json
import requests
import pickle
import os
import datetime

URLS = []

def get_stations(start, end):
  if not os.path.isfile('station_request_%s-%s.pickle' % (start, end)):
    r = requests.get('https://www.umweltbundesamt.de/api/air_data/v2/stations/json?use=airquality&lang=de&date_from='+ start + '&time_from=1&date_to=' + end + '&time_to=24')
    with open('station_request_%s-%s.pickle' % (start, end), 'wb') as handle:
      pickle.dump(r, handle)

  with open('station_request_%s-%s.pickle' % (start, end), 'rb') as handle:
    r = pickle.load(handle)

  return r.json()

def get_station_data(station_id, start, end):
  filename = '%s-data-request-%s-%s.pickle' % (station_id, start, end)
  if not os.path.isfile(filename):
    url = 'https://www.umweltbundesamt.de/api/air_data/v2/airquality/json?date_from='+ start + '&time_from=1&date_to=' + end + '&time_to=24&station='+ station_id + '&lang=de'
    URLS.append(url)
    r = requests.get(url)
    with open(filename, 'wb') as handle:
      pickle.dump(r, handle)

  with open(filename, 'rb') as handle:
    r = pickle.load(handle)

  return r.json()



START = '2019-01-01'
END = '2020-12-31'
stations = get_stations(START, END)

# filter for SH
SH = []
for station_number in stations['data']:
    if stations['data'][station_number][12] == 'SH':
        SH.append(stations['data'][station_number])
print('found %i stations in SH' % SH.__len__())

# Get data points of stations:
feinstaub_data = {}
for station in SH:
  data = get_station_data(station[0], START, END)
  data_points = []
  # check if feinstaub data exists
  for data_point in data['data'][station[0]].items():
    for measurement in data_point[1]:
      if type(measurement) != list:
        continue
      id = measurement[0]
      #1 - feinstaub
      #3 - ozone
      #5 - stickstoff
      if id == 1:
        value = measurement[1]
        data_points.append((data_point[1][0], value))
  if data_points.__len__() > 0:
    feinstaub_data[station[1]] = data_points

# bin data to Calender weeks
CW_19 = CW_20 = {}
for station_name, data in feinstaub_data.items():
  for date, value in data:
    if '2019'in date:
      if '24:' in date:
        date = date.replace('24:', '23:')
      d = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
      cw = d.isocalendar()[1]
      try:
        CW_19[cw].append((station_name, date, value))
      except KeyError:
        CW_19[cw] = []
        CW_19[cw].append((station_name, date, value))
    if '2020'in date:
      if '24:' in date:
        date = date.replace('24:', '23:')
      d = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
      cw = d.isocalendar()[1]
      try:
        CW_20[cw].append((station_name, date, value))
      except KeyError:
        CW_20[cw] = []
        CW_20[cw].append((station_name, date, value))


print(feinstaub_data)
print('ende!')


