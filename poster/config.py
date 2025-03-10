import os

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')

SERVER_PORT = int(os.environ.get('SERVER_PORT', 8080))