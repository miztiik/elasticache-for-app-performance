# -*- coding: utf-8 -*-

import boto3
import redis
import constants

REDIS_HOST = constants.REDIS_HOST
REDIS_PORT = constants.REDIS_PORT

if not REDIS_HOST:
    print(f'REDIS_HOST:{REDIS_HOST} is none')
    exit

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


print("Redis DB size = " + str(r.dbsize()))

print("Completed Successfully!")
