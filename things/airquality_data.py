import datetime


class AirqualityData:
    def __init__(self, station_id, airquality_data_as_list, indices):
        self._indices = indices
        self._raw_data = airquality_data_as_list[station_id]

        self.measurements = []
        for key, value in self._raw_data.items():
            self.measurements.append(AirqualityMeasurement(value))

        self.station_id = station_id

    def __str__(self):
        return "%s" % (self._raw_data)
    
    def __repr__(self):
        return str(self)



class AirqualityMeasurement:
    def __init__(self, as_list):
        # map 24 uhr auf 23:59        
        date = as_list[0].replace('24:00', '23:59')
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.total_index = as_list[1]
        self.data_incomplete = as_list[2]

        self.messung = []
        for item in as_list: 
            if type(item) is list:
                self.messung.append(AirqualityMeasurementDatapoint(item))
        self._raw_data = as_list

    def __str__(self):
        return "%s" % self.messung 
    
    def __repr__(self):
        return str(self)



COMP2ID = { 0: "unkown",
            1: "feinstaub",
            2: "unkown",
            3: "ozone",
            4: "unkown",
            5: "stickstoff",
            }

class AirqualityMeasurementDatapoint:

    def __init__(self, as_list):
        self.component_id = as_list[0]
        self.value = as_list[1]
        self.index = as_list[2]
        self.y_value = as_list[3]

    def __str__(self):
        return "%s" % COMP2ID[self.component_id]

    def __repr__(self):
        return str(self)
