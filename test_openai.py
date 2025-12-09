import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')

print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")
print(f"API Key length: {len(api_key) if api_key else 0}")

# Test the API call
url = 'https://api.openai.com/v1/chat/completions'
payload = {
    'model': 'gpt-5-mini',
    'messages': [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello!"}
    ],
    'max_completion_tokens': 50
}
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print("\nMaking API request...")
try:
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")