"""choice: pick an option from a list. """
from jev import ask

messages = [
    "My package says delivered but I never received it.",
    "I was charged twice for the same order. Can I get a refund?",
    "I can't log in to my account even after resetting my password.",
    "My order arrived damaged and I want a replacement.",
    "Do you have this laptop available in 16GB RAM?"
]

question = {
    "team": {
        "type": "choice",
        "instructions": "Which team should handle this customer message?",
        "criteria": {
            "shipping": "Deliveries, tracking, lost or delayed packages",
            "tech": "Login problems, bugs, account access issues",
            "billing": "Charges, refunds, invoices, payment disputes",
            "sales": "Product availability, pricing, and pre-purchase questions",
            "returns": "Damaged products, replacements, and product returns"
        }
    }
}

def main() -> None:
    for message in messages:
        ans = ask(state=message, questions=question)
        team = ans["team"]
        print(f"{message}\n -> {team['choice']} ({team['confidence']:.0%} confident)\n")


if __name__ == "__main__":
    main()
