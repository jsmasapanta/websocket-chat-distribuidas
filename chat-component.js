class ChatComponent extends HTMLElement {
    constructor() {
        super()

        const shadow = this.attachShadow({ mode: 'open' })

        const template = document.createElement('template')

        template.innerHTML = `
        <style>
            .app {
                display: grid;
                grid-template-columns: 260px 1fr;
                height: 520px;
                border-radius: 18px;
                overflow: hidden;
                background: #e2e8f0;
            }

            .sidebar {
                background: #0f172a;
                color: white;
                padding: 20px;
            }

            .sidebar input {
                width: 100%;
                padding: 10px;
                border-radius: 10px;
                border: none;
                margin-bottom: 10px;
            }

            .sidebar button {
                width: 100%;
                padding: 10px;
                border-radius: 10px;
                border: none;
                background: #38bdf8;
                cursor: pointer;
                font-weight: bold;
            }

            .usuarios {
                margin-top: 20px;
            }

            .usuarios li {
                background: rgba(255,255,255,0.1);
                padding: 8px;
                border-radius: 8px;
                margin-bottom: 5px;
            }

            .chat-area {
            display: grid;
            grid-template-rows: 1fr 70px;
            height: 100%;
            min-height: 0;
}

            .chat {
                height: 100%;
                min-height: 0;
                padding: 20px;
                overflow-y: scroll;
                background: #e2e8f0;
}

            .msg {
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 12px;
                max-width: 70%;
            }

            .own {
                background: #2563eb;
                color: white;
                margin-left: auto;
            }

            .other {
                background: white;
            }

            .system {
                text-align: center;
                font-size: 13px;
                color: #555;
            }

            .input {
                display: flex;
                gap: 10px;
                padding: 15px;
                background: white;
            }

            .input input {
                flex: 1;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ccc;
            }

            .input button {
                padding: 10px 20px;
                border-radius: 10px;
                border: none;
                background: #2563eb;
                color: white;
                cursor: pointer;
            }
        </style>

        <div class="app">
            <div class="sidebar">
                <input id="username" placeholder="Tu nombre">
                <button id="entrar">Entrar</button>

                <div class="usuarios">
                    <h3>Usuarios</h3>
                    <ul id="usuarios"></ul>
                </div>
            </div>

            <div class="chat-area">
                <div class="chat" id="chat"></div>

                <div class="input">
                    <input id="mensaje" placeholder="Mensaje">
                    <button id="enviar">Enviar</button>
                </div>
            </div>
        </div>
        `

        shadow.appendChild(template.content.cloneNode(true))
    }

    connectedCallback() {
        this.socket = io('http://localhost:5000')
        this.username = ''

        const $ = (id) => this.shadowRoot.querySelector(id)

        const chat = $('#chat')
        const usuarios = $('#usuarios')

        $('#entrar').onclick = () => {
            this.username = $('#username').value
            this.socket.emit('set_username', { username: this.username })
        }

        $('#enviar').onclick = () => {

            const msg = $('#mensaje').value.trim()

            if (!msg) return

            // salir del chat
            if (msg === '/salir') {

                this.socket.disconnect()

                this.system(chat, 'Te desconectaste del chat')

                $('#mensaje').disabled = true

                return
            }       

            this.socket.emit('chat_message', { message: msg })

            $('#mensaje').value = ''
            }

        this.socket.on('user_list', (data) => {
            usuarios.innerHTML = ''
            data.users.forEach(u => {
                const li = document.createElement('li')
                li.textContent = u
                usuarios.appendChild(li)
            })
        })

        this.socket.on('chat_message', (data) => {
            const div = document.createElement('div')
            const isOwn = data.username === this.username

            div.id = data.id
            div.className = 'msg ' + (isOwn ? 'own' : 'other')

            div.innerHTML = `
                <b>${isOwn ? 'Tú' : data.username}</b><br>
                ${data.message}<br>
                <small>${data.timestamp}</small>
            `

            chat.appendChild(div)
            chat.scrollTop = chat.scrollHeight
        })

        this.socket.on('user_joined', (d) => {
            this.system(chat, d.username + ' se unió')
        })

        this.socket.on('user_left', (d) => {
            this.system(chat, d.username + ' salió')
        })
        this.socket.on('delete_message', (data) => {
            const mensaje = this.shadowRoot.getElementById(data.id)

            if (mensaje) {
                mensaje.remove()
            }
        })
    }

    system(chat, text) {
        const div = document.createElement('div')
        div.className = 'msg system'
        div.textContent = text
        chat.appendChild(div)
    }
}

customElements.define('chat-component', ChatComponent)