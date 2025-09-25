import mysql.connector
from flask import Flask, jsonify, request

# =======================================
# 1. Creazione app Flask
# =======================================
app = Flask(__name__)

# =======================================
# 2. Configurazione DB MySQL
# =======================================
db_config = {
    'host': 'mysql-30ced52f-iisgalvanimi-cbb0.g.aivencloud.com',
    'user': 'avnadmin',      
    'password': 'AVNS_ROZR4I-u_7cKxsHOkgF',
    'database': 'DistributoriBenzina',
    'port': 14409
}

def get_db_connection():
    """Crea e ritorna una connessione al database MySQL."""
    conn = mysql.connector.connect(**db_config)
    return conn

# =======================================
# 3. Rotte API
# =======================================

# GET tutti distributori
@app.route('/api/distributori', methods=['GET'])
def get_distributori():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM distributori ORDER BY id")
    risultati = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(risultati)

# POST aggiungi distributore
@app.route('/api/distributori', methods=['POST'])
def aggiungi_distributore():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO distributori (nome, indirizzo, citta, provincia, lat, lon, prezzo_benzina, prezzo_diesel)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        data['nome'], data['indirizzo'], data['citta'], data['provincia'],
        float(data['lat']), float(data['lon']),
        float(data.get('prezzo_benzina', 1.85)),
        float(data.get('prezzo_diesel', 1.75))
    ))
    conn.commit()
    nuovo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"messaggio": "Distributore aggiunto", "id": nuovo_id})

# PUT modifica distributore
@app.route('/api/distributori/<int:distributore_id>', methods=['PUT'])
def modifica_distributore(distributore_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE distributori SET nome=%s, indirizzo=%s, citta=%s, provincia=%s,
        lat=%s, lon=%s, prezzo_benzina=%s, prezzo_diesel=%s
        WHERE id=%s
    """
    cursor.execute(query, (
        data['nome'], data['indirizzo'], data['citta'], data['provincia'],
        float(data['lat']), float(data['lon']),
        float(data.get('prezzo_benzina', 1.85)),
        float(data.get('prezzo_diesel', 1.75)),
        distributore_id
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"messaggio": "Distributore modificato"})

# DELETE distributore
@app.route('/api/distributori/<int:distributore_id>', methods=['DELETE'])
def elimina_distributore(distributore_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM distributori WHERE id=%s", (distributore_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"messaggio": "Distributore eliminato"})

# POST cambio prezzi per provincia
@app.route('/api/prezzo/provincia/<string:provincia>', methods=['POST'])
def set_prezzo_provincia(provincia):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    modificati = 0
    query = "UPDATE distributori SET "
    query_parts = []
    params = []

    if 'prezzo_benzina' in data:
        query_parts.append("prezzo_benzina=%s")
        params.append(float(data['prezzo_benzina']))
    if 'prezzo_diesel' in data:
        query_parts.append("prezzo_diesel=%s")
        params.append(float(data['prezzo_diesel']))
    
    if query_parts:
        query += ", ".join(query_parts) + " WHERE provincia=%s"
        params.append(provincia)
        cursor.execute(query, tuple(params))
        modificati = cursor.rowcount
        conn.commit()

    cursor.close()
    conn.close()
    return jsonify({"messaggio": f"Prezzi aggiornati per {modificati} distributori."})

# =======================================
# 4. Esecuzione server
# =======================================
if __name__ == '__main__':
    print("=====================================================")
    print("🚀 API Server in esecuzione sulla porta 5001!")
    print("=====================================================")
    app.run(debug=True, port=5001)
