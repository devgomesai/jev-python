import json
import os

import requests
from dotenv import load_dotenv
load_dotenv()
message = "Hi, I was charged twice for my order last week. Can I get a refund on those?"

resposne = requests.post(
    "https://openrouter.ai/api/alpha/decisions",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json={
        "model": "parallel/decisions-fast:free",
        "state": message,
        "questions": {
            "is_refund": {
                "type": "noul",
                "instructions": "Is the customer asking for a refund?",
                "criteria": {
                    "true": "They want money back.",
                    "false": "They want something else.",
                },
            }
        },
    },
    timeout=60,
)

data = resposne.json()

print(json.dumps(data, indent=2))

ans = data["answers"]["is_refund"]["noul"]
print(f"\n Chance this is a refund request: {ans:.0%}")

if ans > 0.5:
    print("-> Sending to the refund team ")
else:
    print("-> Normal support queue ")
