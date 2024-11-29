from pymongo import MongoClient

# MongoDB connection
#Esta configurada con ip externa de GCP, probablemente toque cambiarla xd
client = MongoClient('mongodb://34.45.86.253:27017/')
db = client["instituciones_db"]
collection = db["instituciones"]
