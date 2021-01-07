import redis
import requests
import json
from datetime import datetime

class Redis(object):
    def __init__(self, redis_store):
        self.redis = redis_store
        self.measurments_count = 0

    def init_patients(self):
        for i in range (1, 7):
            r = requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/' + str(i))
            if r.status_code == 200:
                content = json.loads(r.content)
                table_name = 'user' + str(i)
                self.redis.hset(table_name, 'birthdate', content['birthdate'])
                self.redis.hset(table_name, 'firstname', content['firstname'])
                self.redis.hset(table_name, 'lastname', content['lastname'])
                self.redis.hset(table_name, 'fullname', content['firstname'] + ' ' + content['lastname'])

    def get_patient_personal_data(self, id):
        fullname = self.redis.hgetall('user' + str(id))['fullname']
        birthdate = self.redis.hgetall('user' + str(id))['birthdate']
        return fullname + ' ( ' + birthdate + ' )'

    def save_users_sensor_values(self):
        for i in range (1, 7):
            r = requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/' + str(i))
            if r.status_code == 200:
                content = json.loads(r.content)['trace']['sensors']
                for j in range(len(content)):
                    table_name = 'user' + str(i) + 'sensor' + str(content[j]['id']) + 'measurment' + str(self.measurments_count)
                    self.redis.hset(table_name, 'anomaly', int(content[j]['anomaly']))
                    self.redis.hset(table_name, 'date', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                    self.redis.hset(table_name, 'name', content[j]['name'])
                    self.redis.hset(table_name, 'value', int(content[j]['value']))
        self.measurments_count = self.measurments_count + 1

    def get_user_sensor_values(self, user_id, sensor_id, count):
        data = []
        left = self.measurments_count - count
        right = self.measurments_count
        if left < 0:
            left = 0
        for i in range (left, right):
            table_name = 'user' + str(user_id) + 'sensor' + str(sensor_id) + 'measurment' + str(i)
            data.append(self.redis.hgetall(table_name))
        return data

