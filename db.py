import redis
import requests
import json

class Redis(object):
    def __init__(self, redis_store):
        self.redis = redis_store

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

    def get_patient(self, id):
        print(self.redis.hgetall('user' + str(id)))

