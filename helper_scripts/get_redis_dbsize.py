# -*- coding: utf-8 -*-

import boto3
import redis

REDIS_HOST = redis_stack_configs.REDIS_HOST
REDIS_PORT = redis_stack_configs.REDIS_PORT

if not REDIS_HOST:
    print(f'REDIS_HOST:{REDIS_HOST} is none')
    exit

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


print("Redis DB size = " + str(r.dbsize()))

print("Completed Successfully!")
