import os
import uuid
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from llm_query import get_response
# Load RAG DB requirements
from langchain_community.vectorstores import DeepLake
from langchain_openai import OpenAIEmbeddings

# Global initialization
embeddings = None
db = None
retriever = None
conversational_rag_chain = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

def initialize_deep_lake():
    global embeddings, db, retriever
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", disallowed_special=())
    db = DeepLake(dataset_path=os.getenv("DEEPLAKE_PATH", "./my_deeplake/"), embedding=embeddings, read_only=True)
    # Set RAG access rules
    retriever = db.as_retriever()
    retriever.search_kwargs.update({"distance_metric": "cos", "fetch_k": 120, "k": 5})

@socketio.on('connect')
def handle_connect():
    # Ensure Deep Lake and other components are initialized only once
    if 'loaded' not in session:
        initialize_deep_lake()
        session['loaded'] = True
    if 'user_session_id' not in session:
        session['user_session_id'] = str(uuid.uuid4())

# @app.route('/')
# def index():
    # return render_template('chat.html')  # A basic HTML page with your chat UI

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({'message': 'API is working'})

@socketio.on('message')
def handleMessage(msg):
    global retriever
    session_id = session.get('user_session_id', 'default')
    print('Message: ' + msg, session_id)
    response = get_response(msg, retriever, session_id)
    emit('response', {'data': response})

@socketio.on('disconnect')
def handle_disconnect():
   session.clear()

if __name__ == '__main__':
    socketio.run(app, port=5000)

