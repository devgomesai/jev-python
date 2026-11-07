import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = os.environ['MODEL']


def ask(state, question):
    resposne = requests.post(
        URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={
            "model": MODEL,
            "state": state,
            "questions": question,
        },
        timeout=60,
    )
    resposne.raise_for_status()
    data = resposne.json()
    # print(json.dumps(data, indent=2)) #required for debugging
    return data["answers"]
