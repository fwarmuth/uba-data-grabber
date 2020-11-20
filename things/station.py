class Station:
    def __init__(self, station_as_list, indices):
        self._indices = indices
        self._raw_data = {}
        for index, name in enumerate(self._indices):
            self._raw_data[name] = station_as_list[index]
        
        self.station_id = self._raw_data["station id"]
        self.station_code = self._raw_data["station code"]
        self.network_code = self._raw_data["network code"]
        self.monthly = []

        self.data = []
            

    def __str__(self):
        return "Station Code: %s, data: %s" % (self.station_code, self._raw_data)
    
    def __repr__(self):
        return str(self)



