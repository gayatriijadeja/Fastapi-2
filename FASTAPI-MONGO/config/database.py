from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000")

db = client.PRL_db

collection_name = db["MailInfo"]




