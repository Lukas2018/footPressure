class Config(object):
    def __init__(self, patients_number, sensors_number):
        self.patients_number = patients_number
        self.sensors_number = sensors_number

    def get_patients_number(self):
        return self.patients_number

    def get_sensors_number(self):
        return self.sensors_number