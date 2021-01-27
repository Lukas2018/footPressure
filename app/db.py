import redis
import requests
import json
from datetime import datetime

class Redis(object):
    def __init__(self, redis_store, config):
        self.redis = redis_store
        self.config = config

    def init_patients(self):
        for i in range (1, self.config.get_patients_number() + 1):
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
        data = []
        ok = True
        for i in range (1, self.config.get_patients_number() + 1):
            try:
                r = requests.get('http://tesla.iem.pw.edu.pl:9080/v2/monitor/' + str(i), timeout=5)
                n = self.redis.llen(str(i)) + 1
                if r.status_code == 200:
                    content = json.loads(r.content)['trace']['sensors']
                    data = {
                        str(n): {}
                    }
                    for j in range(len(content)):
                        data[str(n)][str(j)] = {}
                        data[str(n)][str(j)] = {}
                        data[str(n)][str(j)] = {}
                        data[str(n)][str(j)] = {}
                    for j in range(len(content)):
                        data[str(n)][str(j)]['anomaly'] = int(content[j]['anomaly'])
                        data[str(n)][str(j)]['date'] = datetime.now().strftime('%H:%M:%S')
                        data[str(n)][str(j)]['name'] = content[j]['name']
                        data[str(n)][str(j)]['value'] = int(content[j]['value'])
                    self.redis.rpush(str(i), json.dumps(data))
            except requests.ConnectionError:
                return

    def get_user_sensor_data(self, person_id, sensor_id, count=None, key=None):
        data = []
        n = self.redis.llen(str(person_id))
        if count == None:
            count = n
        left = n - count
        right = n
        if left < 0:
            left = 0
        data = self.redis.lrange(str(person_id), left, right)
        results = []
        for i in range (len(data)):
            values = json.loads(data[i])
            values = values[list(values.keys())[0]]
            if key is None:
                results.append(values[str(sensor_id)])
            else:
                results.append(values[str(sensor_id)][key])
        return results