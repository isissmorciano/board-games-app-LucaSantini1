from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime


# Configurazione Flask
app = Flask(__name__)
DATABASE = 'board_games.db'

def init_db():
    """Inizializza il database con lo schema fornito nel README."""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Schema del database
        cursor.execute('''
            CREATE TABLE giochi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                numero_giocatori_massimo INTEGER NOT NULL,
                durata_media INTEGER NOT NULL,
                categoria TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE partite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gioco_id INTEGER NOT NULL,
                data DATE NOT NULL,
                vincitore TEXT NOT NULL,
                punteggio_vincitore INTEGER NOT NULL,
                FOREIGN KEY (gioco_id) REFERENCES giochi (id)
            )
        ''')
        
        # Insert di esempio
        games = [
            ('Catan', 4, 90, 'Strategia'),
            ('Dixit', 6, 30, 'Party'),
            ('Ticket to Ride', 5, 60, 'Strategia')
        ]
        cursor.executemany(
            'INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES (?, ?, ?, ?)',
            games
        )
        
        matches = [
            (1, '2023-10-15', 'Alice', 10),
            (1, '2023-10-22', 'Bob', 12),
            (2, '2023-11-05', 'Charlie', 25),
            (3, '2023-11-10', 'Alice', 8)
        ]
        cursor.executemany(
            'INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (?, ?, ?, ?)',
            matches
        )
        
        conn.commit()
        conn.close()

def get_db_connection():
    """Crea una connessione al database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route: Creare un nuovo gioco
@app.route('/giochi', methods=['POST'])
def create_game():
    """Crea un nuovo gioco da tavolo."""
    data = request.get_json()
    
    required_fields = ['nome', 'numero_giocatori_massimo', 'durata_media', 'categoria']
    if not all(field in data for field in required_fields):
        return jsonify({'error': get_translation('error.invalid_data')}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES (?, ?, ?, ?)',
        (data['nome'], data['numero_giocatori_massimo'], data['durata_media'], data['categoria'])
    )
    conn.commit()
    game_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': game_id, 'message': get_translation('success.created')}), 201

# Route: Visualizzare la lista dei giochi
@app.route('/giochi', methods=['GET'])
def list_games():
    """Restituisce la lista di tutti i giochi."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM giochi')
    games = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(game) for game in games]), 200

# Route: Registrare una partita
@app.route('/giochi/<int:gioco_id>/partite', methods=['POST'])
def create_match(gioco_id):
    """Registra una nuova partita per un gioco."""
    data = request.get_json()
    
    required_fields = ['data', 'vincitore', 'punteggio_vincitore']
    if not all(field in data for field in required_fields):
        return jsonify({'error': get_translation('error.invalid_data')}), 400
    
    # Verificare che il gioco esista
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM giochi WHERE id = ?', (gioco_id,))
    game = cursor.fetchone()
    
    if not game:
        conn.close()
        return jsonify({'error': get_translation('error.not_found')}), 404
    
    # Inserire la partita
    cursor.execute(
        'INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (?, ?, ?, ?)',
        (gioco_id, data['data'], data['vincitore'], data['punteggio_vincitore'])
    )
    conn.commit()
    match_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': match_id, 'message': get_translation('success.created')}), 201

# Route: Visualizzare la lista delle partite di un gioco
@app.route('/giochi/<int:gioco_id>/partite', methods=['GET'])
def list_matches(gioco_id):
    """Restituisce la lista delle partite per un gioco specifico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificare che il gioco esista
    cursor.execute('SELECT * FROM giochi WHERE id = ?', (gioco_id,))
    game = cursor.fetchone()
    
    if not game:
        conn.close()
        return jsonify({'error': get_translation('error.not_found')}), 404
    
    # Ottenere le partite
    cursor.execute('SELECT * FROM partite WHERE gioco_id = ?', (gioco_id,))
    matches = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(match) for match in matches]), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)