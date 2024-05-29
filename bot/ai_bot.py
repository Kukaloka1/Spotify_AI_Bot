import openai
import os  
import logging

openai.api_key = os.getenv('OPENAI_API_KEY')
logging.info('OpenAI API key configurada.')

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

