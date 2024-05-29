import openai
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import random
import os
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for
import logging

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
        logging.info(f'Recomendación de GPT-4: {recommendation}')
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

# Lista de canciones de otros artistas para reproducción aleatoria
other_song_uris = []  # Dejamos esto vacío

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
    if take_break:
        logging.info('Tomando una pausa prolongada')
    return take_break

# Rutas de Flask para manejar la autenticación
@app.route('/')
def login():
    logging.info('Iniciando proceso de autenticación.')
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    logging.info(f'Redirigiendo a URL de autorización: {auth_url}')
    return redirect(auth_url)

@app.route('/callback')
def callback():
    logging.info('Procesando callback de autenticación.')
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    logging.info(f'Código de autenticación recibido: {code}')
    logging.info(f'State recibido: {state}')
    logging.info(f'Error recibido: {error}')
    if code:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        logging.info('Autenticación exitosa, token obtenido.')
        return redirect(url_for('play_music'))
    else:
        logging.error('No se recibió código de autenticación')
        return "Error en el callback de autenticación: no se recibió código de autenticación", 500

@app.route('/callback_debug')
def callback_debug():
    logging.info('Procesando callback de autenticación (Debug).')
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    logging.info(f'Código de autenticación recibido: {code}')
    logging.info(f'State recibido: {state}')
    logging.info(f'Error recibido: {error}')
    return f"Code: {code}, State: {state}, Error: {error}", 200


@app.route('/play_music')
def play_music():
    logging.info('Iniciando reproducción de música.')
    token_info = session.get('token_info')
    if not token_info:
        logging.warning('No se encontró información de token, redirigiendo a login')
        return redirect('/')
    
    proxy = get_data_impulse_proxy()
    sp, device_id = login_and_get_device(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, proxy)
    if sp and device_id:
        for _ in range(100):
            if should_take_long_break():
                human_pause(3600, 7200)
            else:
                song_uri = random.choice(artist_song_uris)
                play_song(sp, song_uri, device_id, proxy)
                if random.random() < 0.1:
                    for _ in range(random.randint(2, 10)):
                        play_song(sp, song_uri, device_id, proxy)
                human_pause(5, 15)
        logging.info('Finalizando reproducción')
        
        prompt = "Dame una recomendación para una canción popular de otro artista para reproducir en Spotify."
        recommendation = get_gpt4_recommendation(prompt)
        if recommendation:
            play_song(sp, recommendation, device_id, proxy)
    else:
        logging.error('No se pudo iniciar sesión en Spotify o no se encontró un dispositivo disponible.')
        return "Error en la reproducción de música", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)






