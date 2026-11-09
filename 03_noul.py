""" noul: basically a yes or no question. """
from jev import ask

messages = [
    "I returned my headphones two weeks ago, but I still haven't received my refund.",
    "My subscription was cancelled, but I was charged again this month.",
    "I received a defective laptop and want my money back.",
    "Can you tell me when my refund of $120 will arrive?",
    "I want to know the status of my replacement order.",
    "My package is delayed. Can you check the delivery status?",
    "I was charged twice for the same transaction.",
    "Can I exchange my shoes for a different size?"
]

question = {
    "is_refund": {
        "type": "noul",
        "instructions": "Determine whether the customer's message is related to a refund.",
        "criteria":{
            "true": "The customer requests a refund case",
            "false" : "The customer asks about things other than refund case"
        }
    }
}

def main() -> None:
    for message in messages:
        ans = ask(state=message, questions=question)
        is_refund = ans["is_refund"]
        print(f"{message}\n -> {'Refund' if is_refund['noul'] > 0.5 else 'Not Refund'}\n")


if __name__ == "__main__":
    main()
