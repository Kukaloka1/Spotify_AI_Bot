import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import random
import os
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for
import logging
import requests
from urllib.parse import urlencode

print("bIT TECH nETWORK wIL RULE THE wOlrd")

# Configuración de logs
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('spotify_bot.log')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

openai.api_key = os.getenv('OPENAI_API_KEY')
logging.info('OpenAI API key configurada.')

# Spotify OAuth settings
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = "user-read-playback-state,user-modify-playback-state"

# Configuración del proxy Data Impulse
def get_data_impulse_proxy():
    proxy = {
        'http': f"http://{os.getenv('DATA_IMPULSE_USER')}:{os.getenv('DATA_IMPULSE_PASS')}@{os.getenv('DATA_IMPULSE_IP')}:{os.getenv('DATA_IMPULSE_PORT')}",
        'https': f"http://{os.getenv('DATA_IMPULSE_USER')}:{os.getenv('DATA_IMPULSE_PASS')}@{os.getenv('DATA_IMPULSE_IP')}:{os.getenv('DATA_IMPULSE_PORT')}"
    }
    logging.info(f'Proxy configurado: {proxy}')
    return proxy

# Función para obtener recomendaciones de GPT-4
def get_gpt4_recommendation(prompt):
    try:
        logging.info('Solicitando recomendación a GPT-4.')
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        recommendation = response.choices[0].message['content'].strip()
        logging.info(f'Recomendación de GPT-4 recibida: {recommendation}')
        return recommendation
    except Exception as e:
        logging.error(f'Error obteniendo recomendación de GPT-4: {e}')
        return None

# Lista de canciones a reproducir del artista principal
artist_song_uris = [
    'spotify:track:6vEZKdUG0ctDr7XsbQUTC7',  # Canción 1
    'spotify:track:5Y1BBTSQEEmAqWFKaWIOkx',  # Canción 2
    'spotify:track:1hJHjZRYCXl8KWWCOywRbp'   # Canción 3
]
logging.info('Lista de canciones del artista principal configurada.')

# Función para simular una pausa humana
def human_pause(min_seconds, max_seconds):
    pause_time = random.uniform(min_seconds, max_seconds)
    logging.info(f'Pausa por {pause_time:.2f} segundos')
    time.sleep(pause_time)

# Función para reproducir una canción
def play_song(sp, song_uri, device_id, proxy):
    try:
        logging.info(f'Intentando reproducir canción: {song_uri}')
        sp.start_playback(device_id=device_id, uris=[song_uri], proxies=proxy)
        logging.info(f'Reproduciendo {song_uri} con proxy {proxy}')
        human_pause(150, 210)
    except Exception as e:
        logging.error(f'Error reproduciendo canción {song_uri}: {e}')

# Función para iniciar sesión y obtener dispositivo
def login_and_get_device(client_id, client_secret, redirect_uri, proxy):
    try:
        logging.info('Intentando iniciar sesión en Spotify.')
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                       client_secret=client_secret,
                                                       redirect_uri=redirect_uri,
                                                       scope=SCOPE))
        devices = sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            logging.info(f'Dispositivo encontrado: {device_id}')
            return sp, device_id
        else:
            logging.warning('No se encontraron dispositivos disponibles')
            return None, None
    except Exception as e:
        logging.error(f'Error iniciando sesión: {e}')
        return None, None

# Función para determinar si es hora de una pausa prolongada
def should_take_long_break():
    current_hour = time.localtime().tm_hour
    take_break = random.random() < 0.1 and (8 <= current_hour <= 22)
    if (8 <= current_hour <= 22) and take_break:
        logging.info('Tomando una pausa prolongada')
    return take_break

# Rutas de Flask para manejar la autenticación
@app.route('/')
def login():
    logging.info('Iniciando proceso de autenticación.')
    state = os.urandom(16).hex()
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        'response_type': 'code',
        'client_id': SPOTIPY_CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': SPOTIPY_REDIRECT_URI,
        'state': state
    })
    logging.info(f'Redirigiendo a URL de autorización: {auth_url}')
    return redirect(auth_url)

@app.route('/callback')
def callback():
    logging.info('Procesando callback de autenticación.')
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    logging.info(f'Código de autenticación recibido: {code}')
    logging.info(f'State recibido: {state}')
    logging.info(f'Error recibido: {error}')
    
    if not code:
        logging.error('No se recibió código de autenticación')
        return "Error en el callback de autenticación: no se recibió código de autenticación", 500
    
    # Solicitar token de acceso
    token_url = "https://accounts.spotify.com/api/token"
    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIPY_REDIRECT_URI,
        "client_id": SPOTIPY_CLIENT_ID,
        "client_secret": SPOTIPY_CLIENT_SECRET
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    logging.info(f'Respuesta del token: {response.json()}')
    
    if response.status_code != 200:
        logging.error(f'Error al obtener token: {response.json()}')
        return "Error al obtener token", 500
    
    session['token_info'] = response.json()
    return redirect(url_for('start_playback'))

@app.route('/start_playback')
def start_playback():
    logging.info('Trigger manual para iniciar la reproducción de música.')
    token_info = session.get('token_info')
    if not token_info:
        logging.warning('No se encontró información de token, redirigiendo a login')
        return redirect('/')
    
    proxy = get_data_impulse_proxy()
    sp, device_id = login_and_get_device(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, proxy)
    if sp and device_id:
        logging.info('Iniciando reproducción de canciones del artista principal.')
        for _ in range(100):
            if should_take_long_break():
                human_pause(3600, 7200)
            else:
                song_uri = random.choice(artist_song_uris)
                logging.info(f'Reproduciendo canción del artista principal: {song_uri}')
                play_song(sp, song_uri, device_id, proxy)
                human_pause(5, 15)
        
        logging.info('Finalizando reproducción de canciones del artista principal.')
        
        prompt = "Dame una recomendación para una canción popular de otro artista para reproducir en Spotify."
        recommendation = get_gpt4_recommendation(prompt)
        if recommendation:
            logging.info(f'Reproduciendo recomendación de GPT-4: {recommendation}')
            play_song(sp, recommendation, device_id, proxy)
    else:
        logging.error('No se pudo iniciar sesión en Spotify o no se encontró un dispositivo disponible.')
        return "Error en la reproducción de música", 500
    
    return "Reproducción de música iniciada."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

















