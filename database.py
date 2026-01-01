from pymongo import MongoClient

# Connection URI
MONGO_URI = "mongodb+srv://anghaejhie_db_user:RGzhVTYB7n5WMMCq@cluster0.w9hvvbp.mongodb.net/?appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Database
db = client['history_pedia']

# Collections
users_collection = db['users']
articles_collection = db['articles']

def get_database():
    return db
