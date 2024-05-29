import os
from flask import request, redirect, session, url_for
import logging
import requests
from urllib.parse import urlencode

def login():
    logging.info('Iniciando proceso de autenticación.')
    state = os.urandom(16).hex()
    auth_url = os.getenv("ACCOUNT_AUTHORIZE") + "?" + urlencode({
        'response_type': 'code',
        'client_id': os.getenv('SPOTIPY_CLIENT_ID'),
        'scope': "user-read-playback-state,user-modify-playback-state",
        'redirect_uri': os.getenv('SPOTIPY_REDIRECT_URI'),
        'state': state
    })
    logging.info('Redirigiendo a URL de autorización')
    return redirect(auth_url)

def callback():
    logging.info('Procesando callback de autenticación.')
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    logging.info(f'Código de autenticación recibido: {code}')
    logging.info(f'State recibido: {state}')
    logging.info(f'Error recibido: {error}')
    
    if error:
        logging.error(f'Error en el callback de autenticación: {error}')
        return f"Error en el callback de autenticación: {error}", 500
    
    if not code:
        logging.error('No se recibió código de autenticación')
        return "Error en el callback de autenticación: no se recibió código de autenticación", 500
    
    # Solicitar token de acceso
    token_url = os.getenv('API_TOKEN_ASK')
    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv('SPOTIPY_REDIRECT_URI'),
        "client_id": os.getenv('SPOTIPY_CLIENT_ID'),
        "client_secret": os.getenv('SPOTIPY_CLIENT_SECRET')
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    logging.info(f'Respuesta del token: {response.json()}')
    
    if response.status_code != 200:
        logging.error(f'Error al obtener token: {response.json()}')
        return "Error al obtener token", 500
    
    session['token_info'] = response.json()
    return redirect(url_for('start_playback'))


