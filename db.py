from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["it_support_chatbot"]
tickets_collection = db["tickets"]
