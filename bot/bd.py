import sqlite3
from datetime import datetime


def create_database():
    '''
    Crea la base de datos si no existe.
    '''
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Crear tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            start_date TEXT
        )
    ''')

    # Crear tabla de chistes y reacciones
    c.execute('''
        CREATE TABLE IF NOT EXISTS jokes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            joke TEXT,
            reaction TEXT,
            timestamp TEXT,
            FOREIGN KEY (chat_id) REFERENCES users (chat_id)
        )
    ''')

    conn.commit()
    conn.close()


def update_reaction(chat_id, reaction):
    '''
    Actualiza la reacción del usuario al último chiste enviado.
    '''
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        UPDATE jokes 
        SET reaction = ?
        WHERE chat_id = ? 
        AND id = (SELECT MAX(id) FROM jokes WHERE chat_id = ?)
    ''', (reaction, chat_id, chat_id))
    conn.commit()
    conn.close()


def save_joke(chat_id, joke):
    '''
    Guarda un chiste enviado al usuario.
    '''
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO jokes (chat_id, joke, timestamp) VALUES (?, ?, ?)',
        (chat_id, joke, datetime.now())
    )
    conn.commit()
    conn.close()


def add_user(chat_id):
    '''
    Agrega un usuario a la base de datos.
    '''
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute(
        'INSERT OR IGNORE INTO users (chat_id, start_date) VALUES (?, ?)',
        (chat_id, datetime.now()))
    conn.commit()
    conn.close()


def remove_user(chat_id):
    '''
    Elimina un usuario de la base de datos.
    '''
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()


def is_user_subscribed(chat_id):
    '''
    Verifica si un usuario está suscrito al bot.
    '''
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM users WHERE chat_id = ?', (chat_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


def get_all_subscribed_users():
    '''
    Devuelve una lista de todos los usuarios suscritos al bot.
    '''
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM users')
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users
