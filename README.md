# 🎵 **BitTech Network Spotify Punk Bot** 🤖

¡Bienvenido al repositorio del Bot de Spotify de **BitTech Network**! Este bot está diseñado para interactuar con la API de Spotify y OpenAI, proporcionando una experiencia musical automatizada e inteligente. Además, hace uso de proxies configurados para mejorar la seguridad y el rendimiento.

## 🎨 **Descripción**

Este bot utiliza `Flask` para manejar la autenticación con Spotify y permite la reproducción automática de una lista de canciones seleccionadas, con pausas simuladas para imitar el comportamiento humano. Además, aprovecha la API de OpenAI para obtener recomendaciones de canciones populares, añadiendo un toque de inteligencia artificial a tu experiencia musical. Los proxies son servidos por **DataImpulse** para garantizar la seguridad y el rendimiento.

## 🚀 **Funcionalidades**

- **🔒 Autenticación con Spotify**: Utiliza OAuth 2.0 para iniciar sesión de forma segura en Spotify.
- **🎶 Reproducción de Canciones**: Reproduce una lista de canciones seleccionadas del artista principal, con la opción de incluir canciones de otros artistas basadas en recomendaciones de GPT-4.
- **⏸️ Pausas Simuladas**: Incluye pausas aleatorias para simular el comportamiento humano durante la reproducción de música.
- **🛡️ Uso de Proxies**: Configura y utiliza proxies de **DataImpulse** para manejar las solicitudes de red de forma segura y eficiente.
- **📋 Registros Detallados**: Implementa un sistema de logs para monitorear y depurar la actividad del bot.
- **🤖 Recomendaciones de IA**: Utiliza la API de OpenAI para obtener recomendaciones de canciones populares, haciendo que la experiencia musical sea más variada e interesante.

## ⚙️ **Configuración**

1. **Clona el repositorio**:
    ```sh
    git clone https://github.com/tu-usuario/bittech-spotify-bot.git
    cd bittech-spotify-bot
    ```

2. **Instala las dependencias**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Configura las variables de entorno**:
   Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
    ```env
    OPENAI_API_KEY=tu_openai_api_key
    SPOTIPY_CLIENT_ID=tu_spotify_client_id
    SPOTIPY_CLIENT_SECRET=tu_spotify_client_secret
    SPOTIPY_REDIRECT_URI=tu_spotify_redirect_uri
    DATA_IMPULSE_USER=tu_usuario_data_impulse
    DATA_IMPULSE_PASS=tu_contraseña_data_impulse
    PROXY_HOST=tu_ip_data_impulse
    PROXY_PORT=tu_puerto_data_impulse
    ```

4. **Ejecuta la aplicación**:
    ```sh
    python app.py
    ```

## 📚 **Uso**

### 🔑 **Autenticación**

Visita `http://localhost:5000/` para iniciar el proceso de autenticación con Spotify. Serás redirigido a la página de autorización de Spotify. Una vez autenticado, serás redirigido a la ruta `/play_music`, donde comenzará la reproducción de música.

### 🎧 **Reproducción de Música**

El bot reproducirá canciones de la lista configurada, simulando pausas humanas. También solicitará recomendaciones de canciones populares a la API de GPT-4 y las reproducirá.

### 🌐 **Rutas de Flask**

- **`/`**: Inicia el proceso de autenticación con Spotify.
- **`/callback`**: Procesa el callback de autenticación de Spotify.
- **`/play_music`**: Inicia la reproducción de música utilizando la API de Spotify y GPT-4.

## 🗂️ **Estructura del Proyecto**

```plaintext
.
├── app.py                 # Archivo principal de la aplicación Flask
├── .env                   # Archivo de variables de entorno
├── requirements.txt       # Dependencias del proyecto
├── spotify_bot.log        # Archivo de logs
├── bot/
│   ├── __init__.py        # Inicialización del paquete bot
│   ├── ai_bot.py          # Interacción con la API de GPT-4
│   ├── auth.py            # Manejo de autenticación con Spotify
│   ├── proxy.py           # Configuración del proxy
│   ├── spotify_bot.py     # Lógica principal del bot de Spotify
│   └── songs.py           # Manejo de canciones
└── README.md              # Este archivo README
📝 Licencia
Este proyecto es de código cerrado y todos los derechos están reservados por BitTech Network.

BitTech Network
www.bittechnetwork.com