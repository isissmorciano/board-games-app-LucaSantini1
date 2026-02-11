from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'board_games.db'

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE giochi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            numero_giocatori_massimo INTEGER NOT NULL,
            durata_media INTEGER NOT NULL,
            categoria TEXT NOT NULL
        )''')
        
        c.execute('''CREATE TABLE partite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gioco_id INTEGER NOT NULL,
            data DATE NOT NULL,
            vincitore TEXT NOT NULL,
            punteggio_vincitore INTEGER NOT NULL,
            FOREIGN KEY (gioco_id) REFERENCES giochi (id)
        )''')
        
        c.executemany('INSERT INTO giochi VALUES (NULL, ?, ?, ?, ?)', [
            ('Catan', 4, 90, 'Strategia'),
            ('Dixit', 6, 30, 'Party'),
            ('Ticket to Ride', 5, 60, 'Strategia')
        ])
        
        c.executemany('INSERT INTO partite VALUES (NULL, ?, ?, ?, ?)', [
            (1, '2023-10-15', 'Alice', 10),
            (1, '2023-10-22', 'Bob', 12),
            (2, '2023-11-05', 'Charlie', 25),
            (3, '2023-11-10', 'Alice', 8)
        ])
        
        conn.commit()
        conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/giochi', methods=['POST'])
def create_gioco():
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES (?, ?, ?, ?)',
              (data['nome'], data['numero_giocatori_massimo'], data['durata_media'], data['categoria']))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/giochi', methods=['GET'])
def list_giochi():
    conn = get_db()
    giochi = conn.execute('SELECT * FROM giochi').fetchall()
    conn.close()
    return jsonify([dict(g) for g in giochi])

@app.route('/giochi/<int:gioco_id>/partite', methods=['POST'])
def create_partita(gioco_id):
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (?, ?, ?, ?)',
              (gioco_id, data['data'], data['vincitore'], data['punteggio_vincitore']))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/giochi/<int:gioco_id>/partite', methods=['GET'])
def list_partite(gioco_id):
    conn = get_db()
    partite = conn.execute('SELECT * FROM partite WHERE gioco_id = ?', (gioco_id,)).fetchall()
    conn.close()
    return jsonify([dict(p) for p in partite])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
