import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('SERPER_API_KEY')
url = 'https://google.serper.dev/search'
headers = {'X-API-KEY': key, 'Content-Type': 'application/json'}
payload = {'q': 'OpenAI', 'num': 5}

try:
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    print('status_code:', r.status_code)
    try:
        data = r.json()
        # Print summary of response structure, not raw content
        print('keys:', list(data.keys()))
        print('organic_length:', len(data.get('organic', [])))
    except Exception as e:
        print('json_parse_error:', e)
        print('text:', r.text[:500])
except Exception as e:
    print('request_error:', e)
