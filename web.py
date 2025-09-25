import json
import requests
from flask import Flask, request, redirect, url_for, flash, get_flashed_messages

API_URL = "http://127.0.0.1:5001/api/distributori"
API_PRICE_URL = "http://127.0.0.1:5001/api/prezzo/provincia"

app = Flask(__name__)
app.secret_key = 'una_chiave_segreta_per_i_messaggi'

@app.route('/', methods=['GET'])
def home():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        dati_distributori = response.json()
        # Converti prezzi e coordinate in float
        for d in dati_distributori:
            d['prezzo_benzina'] = float(d['prezzo_benzina'])
            d['prezzo_diesel'] = float(d['prezzo_diesel'])
            d['lat'] = float(d['lat'])
            d['lon'] = float(d['lon'])
    except requests.exceptions.RequestException as e:
        flash(f"Errore nel connettersi al server API: {e}", "danger")
        dati_distributori = []

    province = sorted(list(set(d['provincia'] for d in dati_distributori)))
    opzioni_province = "".join([f'<option value="{p}">{p}</option>' for p in province])

    lista_html = ""
    for d in dati_distributori:
        lista_html += f'''
        <li class="list-group-item">
            <b>{d['id']}. {d['nome']} ({d['provincia']})</b><br>
            <small>
                Benzina: {d['prezzo_benzina']:.3f}€ - Diesel: {d['prezzo_diesel']:.3f}€
            </small>
            <div class="mt-2">
                <form action="/elimina-distributore" method="POST" style="display:inline-block;">
                    <input type="hidden" name="id" value="{d['id']}">
                    <button class="btn btn-sm btn-danger">Elimina</button>
                </form>
                <button class="btn btn-sm btn-warning" onclick="modificaDistributore({d['id']})">Modifica</button>
            </div>
        </li>
        '''

    flashed_messages = get_flashed_messages(with_categories=True)
    alert_html = "".join([f'<div class="alert alert-{cat}">{msg}</div>' for cat, msg in flashed_messages])

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
                    <div class="card shadow-sm mb-4">
                        <div class="card-header"><h3>Cambia Prezzi per Provincia</h3></div>
                        <div class="card-body">
                            <form action="/cambia-prezzo" method="POST">
                                <select name="provincia" class="form-select mb-2">{opzioni_province}</select>
                                <input type="number" step="0.001" name="prezzo_benzina" class="form-control mb-2" placeholder="Prezzo Benzina">
                                <input type="number" step="0.001" name="prezzo_diesel" class="form-control mb-2" placeholder="Prezzo Diesel">
                                <button type="submit" class="btn btn-primary w-100">Applica Modifiche</button>
                            </form>
                        </div>
                    </div>
                    <div class="card shadow-sm mb-4">
                        <div class="card-header"><h3>Aggiungi Distributore</h3></div>
                        <div class="card-body">
                            <form action="/aggiungi-distributore" method="POST">
                                <input class="form-control mb-2" name="nome" placeholder="Nome">
                                <input class="form-control mb-2" name="indirizzo" placeholder="Indirizzo">
                                <input class="form-control mb-2" name="citta" placeholder="Città">
                                <input class="form-control mb-2" name="provincia" placeholder="Provincia">
                                <input class="form-control mb-2" name="lat" placeholder="Latitudine">
                                <input class="form-control mb-2" name="lon" placeholder="Longitudine">
                                <input class="form-control mb-2" name="prezzo_benzina" placeholder="Prezzo Benzina">
                                <input class="form-control mb-2" name="prezzo_diesel" placeholder="Prezzo Diesel">
                                <button type="submit" class="btn btn-success w-100">Aggiungi</button>
                            </form>
                        </div>
                    </div>
                    <div class="card shadow-sm">
                        <div class="card-header"><h3>Elenco Distributori</h3></div>
                        <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                            <ul class="list-group list-group-flush">{lista_html}</ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([41.9, 12.5], 5.5);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; OpenStreetMap contributors'
            }}).addTo(map);

            var distributori = {json.dumps(dati_distributori)};
            distributori.forEach(d => {{
                L.marker([parseFloat(d.lat), parseFloat(d.lon)])
                    .addTo(map)
                    .bindPopup(`<b>${{d.nome}}</b><br>Benzina: ${{parseFloat(d.prezzo_benzina).toFixed(3)}}€<br>Diesel: ${{parseFloat(d.prezzo_diesel).toFixed(3)}}€`);
            }});

            function modificaDistributore(id) {{
                alert('Funzione modifica per distributore ID: ' + id);
            }}
        </script>
    </body>
    </html>
    '''
    return html_content

# =======================================
# Rotte POST
# =======================================
@app.route('/cambia-prezzo', methods=['POST'])
def cambia_prezzo_web():
    provincia = request.form.get('provincia')
    prezzo_benzina = request.form.get('prezzo_benzina')
    prezzo_diesel = request.form.get('prezzo_diesel')

    payload = {}
    if prezzo_benzina: payload['prezzo_benzina'] = prezzo_benzina
    if prezzo_diesel: payload['prezzo_diesel'] = prezzo_diesel

    if payload:
        try:
            response = requests.post(f"{API_PRICE_URL}/{provincia}", json=payload)
            response.raise_for_status()
            flash(f"Prezzi per {provincia} aggiornati!", "success")
        except requests.exceptions.RequestException as e:
            flash(f"Errore aggiornamento prezzi: {e}", "danger")
    else:
        flash("Nessun prezzo inserito.", "warning")
    return redirect(url_for('home'))

@app.route('/aggiungi-distributore', methods=['POST'])
def aggiungi_distributore_web():
    data = {
        "nome": request.form['nome'],
        "indirizzo": request.form['indirizzo'],
        "citta": request.form['citta'],
        "provincia": request.form['provincia'],
        "lat": request.form['lat'],
        "lon": request.form['lon'],
        "prezzo_benzina": request.form['prezzo_benzina'],
        "prezzo_diesel": request.form['prezzo_diesel']
    }
    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        flash("Distributore aggiunto con successo!", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Errore aggiunta distributore: {e}", "danger")
    return redirect(url_for('home'))

@app.route('/elimina-distributore', methods=['POST'])
def elimina_distributore_web():
    id_distributore = request.form.get('id')
    try:
        response = requests.delete(f"{API_URL}/{id_distributore}")
        response.raise_for_status()
        flash("Distributore eliminato!", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Errore eliminazione distributore: {e}", "danger")
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("🌐 Web Server in esecuzione sulla porta 5000")
    app.run(debug=True, port=5000)
