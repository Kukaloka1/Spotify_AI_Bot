import openai
import os
from dotenv import load_dotenv
from flask import Flask
import logging
from urllib.parse import urlencode
from bot.proxy import get_data_impulse_proxy
from bot.auth import login, callback
from bot.spotify_bot import start_playback

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

# Cargar variables de entorno desde .env
load_dotenv()

# Importar y configurar el proxy
proxy = get_data_impulse_proxy()

# Configurar el proxy globalmente para requests
os.environ['HTTP_PROXY'] = proxy['http']
os.environ['HTTPS_PROXY'] = proxy['https']

app = Flask(__name__)
app.secret_key = os.urandom(24)

openai.api_key = os.getenv('OPENAI_API_KEY')
logging.info('OpenAI API key configurada.')

# Configuración de OAuth de Spotify
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = "user-read-playback-state,user-modify-playback-state"

# Rutas de Flask para manejar la autenticación
app.add_url_rule('/', 'login', login)
app.add_url_rule('/callback', 'callback', callback)
app.add_url_rule('/start_playback', 'start_playback', start_playback)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

