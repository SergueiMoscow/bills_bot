import os

from environs import Env

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

env = Env()
env.read_env(os.path.join(BASE_DIR, '.env'))
BOT_TOKEN = env('BOT_TOKEN')
BILLS_SERVICE_TOKEN = env('BILLS_SERVICE_TOKEN')

AUTHORIZED_USERS = set(env("AUTHORIZED_USERS", "").split(","))
RABBITMQ_URL = env("RABBITMQ_URL")

AUTHORIZED_PATH=env('AUTHORIZED_PATH')
UNAUTHORIZED_PATH=env('UNAUTHORIZED_PATH')
BILLS_SERVICE_URL=env('BILLS_SERVICE_URL')