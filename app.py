from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

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

SYSTEM_PROMPT = """You are a history assistant. ONLY answer questions about history. If asked about non-history topics, say: "Sorry, I only answer history questions." Answer in Indonesian."""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
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
        return jsonify({'response': answer})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)