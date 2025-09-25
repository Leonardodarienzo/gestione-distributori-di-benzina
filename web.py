import json
import requests
from flask import Flask, request, redirect, url_for, flash, get_flashed_messages

# URL del server API
API_URL = "http://127.0.0.1:5001/api/distributori"
API_PRICE_URL = "http://127.0.0.1:5001/api/prezzo/provincia"

# ==============================================================================
# 1. CREAZIONE DELL'APPLICAZIONE FLASK
# ==============================================================================

app = Flask(__name__)
app.secret_key = 'una_chiave_segreta_per_i_messaggi'

# ==============================================================================
# 2. ROTTE WEB (per l'interfaccia utente)
# ==============================================================================

@app.route('/', methods=['GET'])
def home():
    """Pagina principale con gestione distributori."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        dati_distributori = response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Errore nel connettersi al server API: {e}", "danger")
        dati_distributori = []

    province = sorted(list(set(d['provincia'] for d in dati_distributori)))
    opzioni_province = "".join([f'<option value="{p}">{p}</option>' for p in province])

    # Tabella con bottoni Modifica/Elimina
    lista_html = "".join([f'''
        <li class="list-group-item">
            <b>{d['id']}. {d['nome']} ({d['provincia']})</b><br>
            <small>
                Benzina: {d['prezzo_benzina']:.3f}€ - Liv: {d['livello_benzina']}L<br>
                Diesel: {d['prezzo_diesel']:.3f}€ - Liv: {d['livello_diesel']}L
            </small><br>
            <form action="/modifica-distributore/{d['id']}" method="POST" class="d-inline">
                <button type="submit" class="btn btn-sm btn-warning">✏️ Modifica</button>
            </form>
            <form action="/elimina-distributore/{d['id']}" method="POST" class="d-inline">
                <button type="submit" class="btn btn-sm btn-danger">🗑️ Elimina</button>
            </form>
        </li>
    ''' for d in dati_distributori])

    flashed_messages = get_flashed_messages(with_categories=True)
    alert_html = "".join([f'<div class="alert alert-{c}">{m}</div>' for c, m in flashed_messages])

    # HTML completo
    # --- dentro la funzione home(), dove c'è l'HTML ---
html_content = f'''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Monitor Iperstaroil</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <style> #map {{ height: 600px; }} </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="mb-4 text-center">Dashboard Monitoraggio Iperstaroil ⛽</h1>
        {alert_html}
        <div class="row">
            <div class="col-md-8">
                <div class="card shadow-sm">
                    <div class="card-header"><h3>Mappa Distributori</h3></div>
                    <div class="card-body"><div id="map"></div></div>
                </div>
            </div>
            <div class="col-md-4">
                <!-- Cambia prezzi -->
                <div class="card shadow-sm mb-4">
                    <div class="card-header"><h3>Cambia Prezzi per Provincia</h3></div>
                    <div class="card-body">
                        <form action="/cambia-prezzo" method="POST">
                            <div class="mb-3">
                                <label class="form-label">Provincia</label>
                                <select name="provincia" class="form-select">{opzioni_province}</select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Nuovo Prezzo Benzina</label>
                                <input type="number" step="0.001" name="prezzo_benzina" class="form-control">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Nuovo Prezzo Diesel</label>
                                <input type="number" step="0.001" name="prezzo_diesel" class="form-control">
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Applica Modifiche</button>
                        </form>
                    </div>
                </div>

                <!-- ➕ Aggiungi distributore -->
                <div class="card shadow-sm mb-4">
                    <div class="card-header"><h3>Aggiungi Distributore</h3></div>
                    <div class="card-body">
                        <form action="/aggiungi-distributore" method="POST">
                            <input type="text" name="nome" class="form-control mb-2" placeholder="Nome" required>
                            <input type="text" name="indirizzo" class="form-control mb-2" placeholder="Indirizzo" required>
                            <input type="text" name="citta" class="form-control mb-2" placeholder="Città" required>
                            <input type="text" name="provincia" class="form-control mb-2" placeholder="Provincia" required>
                            <input type="number" step="0.0001" name="lat" class="form-control mb-2" placeholder="Latitudine" required>
                            <input type="number" step="0.0001" name="lon" class="form-control mb-2" placeholder="Longitudine" required>
                            <button type="submit" class="btn btn-success w-100">Aggiungi</button>
                        </form>
                    </div>
                </div>

                <!-- ✏️ Modifica distributore -->
                <div class="card shadow-sm mb-4">
                    <div class="card-header"><h3>Modifica Distributore</h3></div>
                    <div class="card-body">
                        <form action="/modifica-distributore" method="POST">
                            <input type="number" name="id" class="form-control mb-2" placeholder="ID Distributore" required>
                            <input type="text" name="nome" class="form-control mb-2" placeholder="Nuovo Nome (opzionale)">
                            <input type="text" name="indirizzo" class="form-control mb-2" placeholder="Nuovo Indirizzo (opzionale)">
                            <input type="text" name="citta" class="form-control mb-2" placeholder="Nuova Città (opzionale)">
                            <input type="text" name="provincia" class="form-control mb-2" placeholder="Nuova Provincia (opzionale)">
                            <button type="submit" class="btn btn-warning w-100">Modifica</button>
                        </form>
                    </div>
                </div>

                <!-- ❌ Elimina distributore -->
                <div class="card shadow-sm mb-4">
                    <div class="card-header"><h3>Elimina Distributore</h3></div>
                    <div class="card-body">
                        <form action="/elimina-distributore" method="POST">
                            <input type="number" name="id" class="form-control mb-2" placeholder="ID Distributore" required>
                            <button type="submit" class="btn btn-danger w-100">Elimina</button>
                        </form>
                    </div>
                </div>

                <!-- Elenco -->
                <div class="card shadow-sm">
                    <div class="card-header"><h3>Elenco Distributori</h3></div>
                    <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                        <ul class="list-group list-group-flush">{lista_html}</ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    ...
</body>
</html>
'''

    return html_content

# ==============================================================================
# 3. AZIONI CRUD DAL FRONTEND
# ==============================================================================

@app.route('/aggiungi-distributore', methods=['POST'])
def aggiungi_distributore():
    dati = {
        "nome": request.form['nome'],
        "provincia": request.form['provincia'],
        "lat": float(request.form['lat']),
        "lon": float(request.form['lon']),
        "prezzo_benzina": float(request.form['prezzo_benzina']),
        "prezzo_diesel": float(request.form['prezzo_diesel']),
        "livello_benzina": 0,
        "livello_diesel": 0
    }
    try:
        r = requests.post(API_URL, json=dati)
        r.raise_for_status()
        flash("Distributore aggiunto con successo ✅", "success")
    except Exception as e:
        flash(f"Errore: {e}", "danger")
    return redirect(url_for('home'))

@app.route('/modifica-distributore/<int:id>', methods=['POST'])
def modifica_distributore(id):
    nuovo_prezzo = 1.999  # esempio statico, si può sostituire con un form dedicato
    try:
        r = requests.put(f"{API_URL}/{id}", json={"prezzo_benzina": nuovo_prezzo})
        r.raise_for_status()
        flash(f"Distributore {id} modificato ✏️", "warning")
    except Exception as e:
        flash(f"Errore: {e}", "danger")
    return redirect(url_for('home'))

@app.route('/elimina-distributore/<int:id>', methods=['POST'])
def elimina_distributore(id):
    try:
        r = requests.delete(f"{API_URL}/{id}")
        r.raise_for_status()
        flash(f"Distributore {id} eliminato 🗑️", "danger")
    except Exception as e:
        flash(f"Errore: {e}", "danger")
    return redirect(url_for('home'))

# ==============================================================================

if __name__ == '__main__':
    print("=====================================================")
    print("🌐 Web Server in esecuzione sulla porta 5000!")
    print("=====================================================")
    app.run(debug=True, port=5000)
