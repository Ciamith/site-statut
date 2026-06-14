import socket
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)
DB_NAME = "logs.db"

# Настройки UDP для отправки на Arduino
ARDUINO_IP = "192.168.1.50"  # IP-адрес вашей Arduino/ESP32 в сети
ARDUINO_PORT = 8888          # Порт, который слушает Arduino

# Функция инициализации базы данных SQLite
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS status_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Функция записи действия в базу данных
def log_action(action):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO status_logs (action, timestamp) VALUES (?, ?)", (action, current_time))
    conn.commit()
    conn.close()

# Функция отправки команды по протоколу UDP
def send_udp_command(command):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command.encode('utf-8'), (ARDUINO_IP, ARDUINO_PORT))
        sock.close()
    except Exception as e:
        print(f"Ошибка отправки UDP: {e}")

# Инициализируем базу данных при запуске сервера
init_db()

# --- МАРШРУТЫ СЕРВЕРА ---

@app.route("/")
def index():
    html_page = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Robot Hand Controller</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #121620;
                color: white;
            }
            .container {
                text-align: center;
                background: #1a202c;
                padding: 40px 30px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 90%;
            }
            h1 {
                font-size: 18px;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #a0aec0;
                margin-bottom: 30px;
            }
            .btn-container {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-bottom: 25px;
            }
            .btn {
                flex: 1;
                padding: 15px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                text-transform: uppercase;
                text-decoration: none;
                color: white;
                transition: transform 0.1s;
                display: inline-block;
                text-align: center;
            }
            .btn:active { transform: scale(0.95); }
            .btn-on { background-color: #00c851; }
            .btn-off { background-color: #ff3547; }
            .footer-text { font-size: 12px; color: #718096; line-height: 1.5; }
            .footer-text a { color: #00c851; text-decoration: none; }
            iframe { display: none; }
        </style>
    </head>
    <body>

        <div class="container">
            <h1>Robot Hand Control</h1>
            
            <div class="btn-container">
                <a href="/on" target="hidden-form" class="btn btn-on">Открыть (ON)</a>
                <a href="/off" target="hidden-form" class="btn btn-off">Закрыть (OFF)</a>
            </div>

            <div class="footer-text">
                Команды отправляются по UDP протоколу.<br>
                <a href="/logs" target="_blank">Открыть журнал действий (БД)</a>
            </div>
        </div>

        <iframe name="hidden-form"></iframe>

    </body>
    </html>
    """
    return render_template_string(html_page)

@app.route("/on")
def turn_on():
    send_udp_command("ON")
    log_action("ON")
    return "OK"

@app.route("/off")
def turn_off():
    send_udp_command("OFF")
    log_action("OFF")
    return "OK"

@app.route("/logs")
def show_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, action, timestamp FROM status_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    table_rows = ""
    for row in rows:
        table_rows += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"

    html_logs = f"""
    <html>
    <head>
        <title>Журнал действий</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #121620; color: white; padding: 20px; }}
            table {{ width: 100%; max-width: 600px; margin: 0 auto; border-collapse: collapse; background: #1a202c; }}
            th, td {{ padding: 12px; border: 1px solid #2d3748; text-align: left; }}
            th {{ background: #2d3748; color: #a0aec0; }}
            h2 {{ text-align: center; color: #a0aec0; }}
        </style>
    </head>
    <body>
        <h2>История команд из базы данных SQLite</h2>
        <table>
            <tr><th>ID</th><th>Действие</th><th>Время</th></tr>
            {table_rows}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_logs)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
