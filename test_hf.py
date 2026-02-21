import requests
import os

# Router endpoint HF terbaru
API_URL = "https://router.huggingface.co/hf-inference/models/tiiuae/falcon-7b-instruct"

headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
    "Content-Type": "application/json"
}

def query(prompt):
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 150}
        }
    )
    print("Status code:", response.status_code)
    print("Raw text:", response.text)
    return response.json()

prompt = "Kamu adalah analis bisnis UMKM. Berikan insight kenapa revenue bisa turun 3 hari terakhir."

output = query(prompt)

print("\n\nAI Response:\n", output)