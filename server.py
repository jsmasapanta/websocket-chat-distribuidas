from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
import uuid
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

usuarios = {}

@app.route('/')
def index():
    return "<h1>Bienvenidos a mi chat en tiempo real</h1>"

@socketio.on('connect')
def handle_connect():
    print(f'Nuevo cliente conectado: {request.sid}')

@socketio.on("set_username")
def handle_set_username(data):
    username = data.get('username', 'Anónimo')
    usuarios[request.sid] = username
    emit("user_joined", {"username": username}, broadcast=True, include_self=False)
    emit("user_list", {"users": list(usuarios.values())}, broadcast=True)

@socketio.on("chat_message")
def handle_send_message(data):
    username = usuarios.get(request.sid, 'Anónimo')
    message = data.get('message', '')
    timestamp = datetime.now().strftime("%H:%M:%S")
    message_id = str(uuid.uuid4())

    mensaje = {
        "id": message_id,
        "username": username,
        "message": message,
        "timestamp": timestamp
    }

    emit("chat_message", mensaje, broadcast=True)
    emit("message_status", {
        "id": message_id,
        "status": "recibido"
    })

    socketio.start_background_task(delete_message_later, message_id)

def delete_message_later(message_id):
    time.sleep(30)
    socketio.emit(
        "delete_message",
        {"id": message_id}
    )

@socketio.on('disconnect')
def handle_disconnect():
    username = usuarios.pop(request.sid, 'Anónimo')
    print(f'Cliente desconectado: {request.sid} ({username})')
    emit("user_left", {"username": username}, broadcast=True)
    emit("user_list", {"users": list(usuarios.values())}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000, debug=True)