from pymongo import MongoClient

# MongoDB connection
#Esta configurada con ip externa de GCP, probablemente toque cambiarla xd
client = MongoClient('mongodb://104.197.114.21:27017/')
db = client["instituciones-db-gcp"]
collection = db["instituciones"]
