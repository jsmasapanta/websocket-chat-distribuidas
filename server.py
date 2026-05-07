from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

usuarios = {}
registrados = {}

@app.route('/')
def index():
    return "<h1>Bienvenidos a mi chat en tiempo real</h1>"

@socketio.on('connect')
def handle_connect():
    print(f'Nuevo cliente conectado: {request.sid}')

@socketio.on("set_username")
def handle_set_username(data):
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if username == '' or password == '':
        emit("auth_error", {"message": "Debe ingresar usuario y clave"})
        return

    if username not in registrados:
        registrados[username] = generate_password_hash(password)
    else:
        if not check_password_hash(registrados[username], password):
            emit("auth_error", {"message": "Clave incorrecta"})
            return

    usuarios[request.sid] = username

    emit("auth_success", {"username": username})
    emit("user_joined", {"username": username}, broadcast=True, include_self=False)
    emit("user_list", {"users": list(usuarios.values())}, broadcast=True)

@socketio.on("chat_message")
def handle_send_message(data):
    username = usuarios.get(request.sid)

    if not username:
        emit("auth_error", {"message": "Debe iniciar sesión primero"})
        return

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
        "status": "enviado"
    })

    socketio.start_background_task(delete_message_later, message_id)

def delete_message_later(message_id):
    time.sleep(30)
    socketio.emit("delete_message", {"id": message_id})

@socketio.on('disconnect')
def handle_disconnect():
    username = usuarios.pop(request.sid, 'Anónimo')
    print(f'Cliente desconectado: {request.sid} ({username})')
    emit("user_left", {"username": username}, broadcast=True)
    emit("user_list", {"users": list(usuarios.values())}, broadcast=True)

@socketio.on("message_read")
def handle_message_read(data):
    message_id = data.get("id")
    sender = data.get("sender")

    for sid, username in usuarios.items():
        if username == sender:
            socketio.emit(
                "message_status",
                {
                    "id": message_id,
                    "status": "leido"
                },
                to=sid
            )
            break



if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000, debug=True)