import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener variables de entorno
data_impulse_user = os.getenv('DATA_IMPULSE_USER')
data_impulse_pass = os.getenv('DATA_IMPULSE_PASS')
proxy_host = os.getenv('PROXY_HOST')
proxy_port = os.getenv('PROXY_PORT')

def get_data_impulse_proxy():
    if not all([data_impulse_user, data_impulse_pass, proxy_host, proxy_port]):
        logging.error("Una o más variables de entorno para la configuración del proxy no están definidas.")
        raise ValueError("Faltan variables de entorno para la configuración del proxy.")
    
    proxy = {
        'http': f"http://{data_impulse_user}:{data_impulse_pass}@{proxy_host}:{proxy_port}",
        'https': f"http://{data_impulse_user}:{data_impulse_pass}@{proxy_host}:{proxy_port}"
    }
    logging.info(f'Proxy configurado: {proxy}')
    return proxy


