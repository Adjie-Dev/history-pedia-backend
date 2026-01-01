from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

load_dotenv()

app = Flask(__name__)

# Whitelist origins
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    os.environ.get('FRONTEND_URL', 'https://hsitorypedia.vercel.app')
]
CORS(app, origins=allowed_origins)

# Initialize Cerebras client
cerebras_api_key = os.getenv('CEREBRAS_API_KEY')
if not cerebras_api_key:
    raise ValueError("CEREBRAS_API_KEY not found in environment variables")

client = Cerebras(api_key=cerebras_api_key)

# Initialize MongoDB
mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://anghaejhie_db_user:RGzhVTYB7n5WMMCq@cluster0.w9hvvbp.mongodb.net/?appName=Cluster0')
mongo_client = MongoClient(mongo_uri)
db = mongo_client['history_pedia']

# Collections
chat_history_collection = db['chat_history']
users_collection = db['users']

SYSTEM_PROMPT = """You are a history assistant. ONLY answer questions about history. If asked about non-history topics, say: "Sorry, I only answer history questions." Answer in Indonesian."""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')  # Optional: track user
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get AI response
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b",
            max_completion_tokens=1024,
            temperature=0.2,
            top_p=1,
            stream=False
        )
        
        answer = completion.choices[0].message.content
        
        # Save to MongoDB
        chat_record = {
            "user_id": user_id,
            "user_message": user_message,
            "ai_response": answer,
            "timestamp": datetime.utcnow(),
            "model": "llama-3.3-70b"
        }
        chat_history_collection.insert_one(chat_record)
        
        return jsonify({'response': answer})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Get chat history
@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    try:
        user_id = request.args.get('user_id', 'anonymous')
        limit = int(request.args.get('limit', 50))
        
        history = []
        for chat in chat_history_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit):
            chat['_id'] = str(chat['_id'])
            chat['timestamp'] = chat['timestamp'].isoformat()
            history.append(chat)
        
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Get all chat history (admin)
@app.route('/api/chat/history/all', methods=['GET'])
def get_all_chat_history():
    try:
        limit = int(request.args.get('limit', 100))
        
        history = []
        for chat in chat_history_collection.find().sort("timestamp", -1).limit(limit):
            chat['_id'] = str(chat['_id'])
            chat['timestamp'] = chat['timestamp'].isoformat()
            history.append(chat)
        
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Delete chat history
@app.route('/api/chat/history/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    try:
        result = chat_history_collection.delete_one({"_id": ObjectId(chat_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Chat deleted"}), 200
        return jsonify({"error": "Chat not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# User endpoints
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        data['created_at'] = datetime.utcnow()
        result = users_collection.insert_one(data)
        return jsonify({
            "message": "User created",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = []
        for user in users_collection.find():
            user['_id'] = str(user['_id'])
            user['created_at'] = user['created_at'].isoformat() if 'created_at' in user else None
            users.append(user)
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'database': 'connected'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)