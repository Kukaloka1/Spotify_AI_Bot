import spotipy
import logging
import time
import random
from spotipy.oauth2 import SpotifyOAuth
from bot.ai_bot import get_gpt4_recommendation
from bot.songs import artist_song_uris
import os
from flask import session, redirect

# Configuración de logs
logger = logging.getLogger()

# Función para simular una pausa humana
def human_pause(min_seconds, max_seconds):
    pause_time = random.uniform(min_seconds, max_seconds)
    logging.info(f'Pausa por {pause_time:.2f} segundos')
    time.sleep(pause_time)

# Función para reproducir una canción
def play_song(sp, song_uri, device_id):
    try:
        logging.info(f'Intentando reproducir canción: {song_uri}')
        sp.start_playback(device_id=device_id, uris=[song_uri])
        logging.info(f'Reproduciendo {song_uri}')
        # Esperar a que la canción se reproduzca completamente
        track = sp.track(song_uri)
        duration_ms = track['duration_ms']
        duration_sec = duration_ms / 1000
        logging.info(f'Duración de la canción: {duration_sec:.2f} segundos')
        human_pause(duration_sec, duration_sec + 5)  # Añadir un margen de 5 segundos
    except Exception as e:
        logging.error(f'Error reproduciendo canción {song_uri}: {e}')

# Función para iniciar sesión y obtener dispositivo
def login_and_get_device(client_id, client_secret, redirect_uri):
    try:
        logging.info('Intentando iniciar sesión en Spotify.')
        sp_oauth = SpotifyOAuth(client_id=client_id,
                                client_secret=client_secret,
                                redirect_uri=redirect_uri,
                                scope="user-read-playback-state,user-modify-playback-state")
        sp = spotipy.Spotify(auth_manager=sp_oauth)
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
    take_break = random.random() < 0.05 and (8 <= current_hour <= 22)  # Reducir la probabilidad a 0.05
    if take_break:
        logging.info('Tomando una pausa prolongada')
    return take_break

def start_playback():
    logging.info('Trigger manual para iniciar la reproducción de música.')
    token_info = session.get('token_info')
    if not token_info:
        logging.warning('No se encontró información de token, redirigiendo a login')
        return redirect('/')

    try:
        sp, device_id = login_and_get_device(
            os.getenv('SPOTIPY_CLIENT_ID'), 
            os.getenv('SPOTIPY_CLIENT_SECRET'), 
            os.getenv('SPOTIPY_REDIRECT_URI')
        )
        if sp and device_id:
            logging.info('Iniciando reproducción de canciones del artista principal.')
            for _ in range(100):
                if should_take_long_break():
                    human_pause(3600, 7200)
                else:
                    song_uri = random.choice(artist_song_uris)
                    logging.info(f'Reproduciendo canción del artista principal: {song_uri}')
                    play_song(sp, song_uri, device_id)
                    human_pause(5, 15)
            logging.info('Finalizando reproducción de canciones del artista principal.')
            
            prompt = "Dame una recomendación para una canción popular de otro artista para reproducir en Spotify."
            recommendation = get_gpt4_recommendation(prompt)
            if recommendation:
                logging.info(f'Reproduciendo recomendación de GPT-4: {recommendation}')
                play_song(sp, recommendation, device_id)
        else:
            logging.error('No se pudo iniciar sesión en Spotify o no se encontró un dispositivo disponible.')
            return "Error en la reproducción de música", 500
    except Exception as e:
        logging.error(f'Error en start_playback: {e}', exc_info=True)
        return "Error en la reproducción de música", 500

    return "Reproducción de música iniciada."


