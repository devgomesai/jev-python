"""Raw demo of a Decisions API call: a plain requests.post, no jev.py import."""
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://openrouter.ai/api/alpha/decisions"

message = "Hi, I was charged twice for my order last week. Can I get a refund on those?"

question = {
    "is_refund": {
        "type": "noul",
        "instructions": "Is the customer asking for a refund?",
        "criteria": {
            "true": "They want money back.",
            "false": "They want something else.",
        },
    }
}


def main() -> None:
    response = requests.post(
        URL,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={
            # Same model configuration source as jev.py: the MODEL entry in .env
            "model": os.environ["MODEL"],
            "state": message,
            "questions": question,
        },
        timeout=60,
    )
    # Raise a clear HTTPError on 4xx/5xx instead of failing later on json parsing.
    response.raise_for_status()
    data = response.json()

    print(json.dumps(data, indent=2))

    try:
        ans = data["answers"]["is_refund"]["noul"]
    except KeyError:
        raise RuntimeError(
            f"Unexpected API response, no answers['is_refund']['noul']: {data}"
        ) from None

    print(f"\n Chance this is a refund request: {ans:.0%}")

    if ans > 0.5:
        print("-> Sending to the refund team ")
    else:
        print("-> Normal support queue ")


if __name__ == "__main__":
    main()
