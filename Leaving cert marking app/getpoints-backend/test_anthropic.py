import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')
key = os.environ.get('ANTHROPIC_API_KEY')
print('key exists', bool(key))
payload = {
    'model': 'claude-opus-4-8',
    'messages': [
        {'role': 'user', 'content': 'Write a short sentence.'}
    ],
    'max_tokens': 10,
}
headers = {
    'Content-Type': 'application/json',
    'x-api-key': key,
    'anthropic-version': '2023-06-01',
}
resp = requests.post('https://api.anthropic.com/v1/messages', json=payload, headers=headers)
print(resp.status_code)
print(resp.text)
