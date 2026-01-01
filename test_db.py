from pymongo import MongoClient

# Connection string dari MongoDB Atlas
uri = "mongodb+srv://anghaejhie_db_user:RGzhVTYB7n5WMMCq@cluster0.w9hvvbp.mongodb.net/?appName=Cluster0"

try:
    # Connect ke MongoDB
    client = MongoClient(uri)
    
    # Test connection
    client.admin.command('ping')
    print("✅ Koneksi ke MongoDB berhasil!")
    
    # Bikin database dan collection
    db = client['history_pedia']
    collection = db['test_data']
    
    # Insert test data
    test_data = {
        "name": "Test User",
        "email": "test@example.com",
        "created_at": "2026-01-01"
    }
    
    result = collection.insert_one(test_data)
    print(f"✅ Data berhasil di-insert dengan ID: {result.inserted_id}")
    
    # Read data
    found_data = collection.find_one({"name": "Test User"})
    print(f"✅ Data ditemukan: {found_data}")
    
except Exception as e:
    print(f"❌ Error: {e}")