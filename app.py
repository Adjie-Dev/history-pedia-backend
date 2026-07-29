from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from groq import Groq, RateLimitError
from database import db

load_dotenv()

app = Flask(__name__)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    'https://historypedia.vercel.app'
]
CORS(app, origins=allowed_origins)

groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=groq_api_key)

LLM_MODEL = os.getenv('LLM_MODEL', 'openai/gpt-oss-120b')

SYSTEM_PROMPT = """You are a history assistant. ONLY answer questions about history. If asked about non-history topics, say: "Sorry, I only answer history questions." Answer in Indonesian."""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model=LLM_MODEL,
            max_completion_tokens=1024,
            temperature=0.2,
            top_p=1,
            stream=False
        )
        
        answer = completion.choices[0].message.content
        
        try:
            db.save_chat(user_id, user_message, answer, LLM_MODEL)
        except Exception as db_err:
            print(f"DB save skipped: {db_err}")

        return jsonify({'response': answer})

    except RateLimitError:
        return jsonify({'error': 'Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi.'}), 429

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    try:
        user_id = request.args.get('user_id', 'anonymous')
        limit = int(request.args.get('limit', 50))
        
        history = db.get_history(user_id, limit)
        
        for chat in history:
            chat['timestamp'] = chat['timestamp'].isoformat()
        
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/chat/history/all', methods=['GET'])
def get_all_chat_history():
    try:
        limit = int(request.args.get('limit', 100))
        history = db.get_all_history(limit)
        
        for chat in history:
            chat['timestamp'] = chat['timestamp'].isoformat()
        
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/chat/history/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    try:
        if db.delete_chat(chat_id):
            return jsonify({"message": "Chat deleted"}), 200
        return jsonify({"error": "Chat not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'database': 'mysql'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
