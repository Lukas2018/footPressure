import math

class Stats(object):
    def __init__(self, db):
        self.db = db

    def min(self, user_id, sensor_id, count=None):
        if count == None:
            count = self.db.get_measurments_count()
        sensors = self.db.get_user_sensor_data(user_id, sensor_id, count, 'value')
        min = 1023
        for value in sensors:
            value = int(value)
            if value < min:
                min = value
        return min

    def max(self, user_id, sensor_id, count=None):
        if count == None:
            count = self.db.get_measurments_count()
        sensors = self.db.get_user_sensor_data(user_id, sensor_id, count, 'value')
        max = 0
        for value in sensors:
            value = int(value)
            if value > max:
                max = value
        return max

    def mean(self, user_id, sensor_id, count=None):
        if count == None:
            count = self.db.get_measurments_count()
        sensors = self.db.get_user_sensor_data(user_id, sensor_id, count, 'value')
        sum = 0
        count = 0
        for value in sensors:
            sum = sum + int(value)
            count = count + 1
        mean = round(sum / count, 2)
        return mean

    def rms(self, user_id, sensor_id, count=None):
        if count == None:
            count = self.db.get_measurments_count()
        sensors = self.db.get_user_sensor_data(user_id, sensor_id, count, 'value')
        sum = 0
        count = 0
        for value in sensors:
            sum = sum + pow(int(value), 2)
            count = count + 1
        rms = round(math.sqrt(sum / count), 2)
        return rms
