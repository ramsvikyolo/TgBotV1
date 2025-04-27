import os
from flask import Flask, request
import requests
import json

app = Flask(__name__)

# Load configuration from JSON file
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

def send_message(chat_id, text, reply_markup=None):
    """Send a message to the user with optional inline keyboard."""
    url = f"https://api.telegram.org/bot{CONFIG['token']}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': reply_markup
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates from Telegram."""
    update = request.get_json()
    
    # Handle incoming messages
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        if text in CONFIG['commands']:
            command = CONFIG['commands'][text]
            reply_markup = {'inline_keyboard': CONFIG['buttons'][command['buttons']]}
            send_message(chat_id, command['text'], reply_markup)
    
    # Handle button presses (callback queries)
    elif 'callback_query' in update:
        callback_query = update['callback_query']
        chat_id = callback_query['message']['chat']['id']
        data = callback_query['data']
        if data in CONFIG['responses']:
            send_message(chat_id, CONFIG['responses'][data])
            # Acknowledge the callback query to remove the loading indicator
            callback_query_id = callback_query['id']
            url = f"https://api.telegram.org/bot{CONFIG['token']}/answerCallbackQuery"
            payload = {'callback_query_id': callback_query_id}
            requests.post(url, json=payload)
    
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT, default to 5000 if not set
    app.run(host='0.0.0.0', port=port)
