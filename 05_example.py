from jev import ask

inbox = [
    {
        "id": "TKT-001",
        "subject": "Charged twice for my subscription",
        "message": "I purchased the premium subscription yesterday, but my bank account was charged twice. I want one payment refunded.",
        "customer": "Rahul",
        "order_value": 999,
        "previous_tickets": 2,
    },
    {
        "id": "TKT-002",
        "subject": "Application crashing after update",
        "message": "Ever since the latest update, the application crashes immediately after login. Multiple employees in our organization are experiencing this.",
        "customer": "Priya",
        "order_value": 15000,
        "previous_tickets": 5,
    },
    {
        "id": "TKT-003",
        "subject": "How do I change my email?",
        "message": "I recently changed my email address. Can you guide me through updating it in my account settings?",
        "customer": "Amit",
        "order_value": 499,
        "previous_tickets": 0,
    },
    {
        "id": "TKT-004",
        "subject": "Unauthorized transaction",
        "message": "I noticed a transaction of Rs. 5000 that I did not authorize. I did not make this purchase. Please investigate immediately.",
        "customer": "Sneha",
        "order_value": 5000,
        "previous_tickets": 1,
    },
    {
        "id": "TKT-005",
        "subject": "Feature request",
        "message": "It would be great if you could introduce dark mode and allow users to customize dashboard widgets. This would improve my experience.",
        "customer": "Karan",
        "order_value": 2499,
        "previous_tickets": 0,
    },
    {
        "id": "TKT-006",
        "subject": "Poor customer support experience",
        "message": "I have contacted support three times regarding my missing order. Nobody has resolved my issue. I am extremely disappointed and considering cancelling my subscription.",
        "customer": "Neha",
        "order_value": 7999,
        "previous_tickets": 3,
    },
    {
        "id": "TKT-007",
        "subject": "Order delivery confirmation",
        "message": "I received my order today. Everything looks good. Thank you for the quick delivery!",
        "customer": "Arjun",
        "order_value": 1299,
        "previous_tickets": 0,
    },
    {
        "id": "TKT-008",
        "subject": "Request for enterprise pricing",
        "message": "We are a company with 250 employees looking to purchase your enterprise plan. Please connect us with someone who can discuss bulk pricing.",
        "customer": "Meera",
        "order_value": 250000,
        "previous_tickets": 1,
    },
]

question = {
    "is_urgent": {
        "type": "noul",
        "instructions": "Determine whether this ticket requires immediate operational intervention due to security incidents, unauthorized payments, widespread outages, or critical business disruptions; do not confuse customer frustration or cancellation threats with operational urgency.",
        "criteria": {
            "true": "Security incidents, unauthorized payments, application-wide outages, or critical business disruptions.",
            "false": "General inquiries, feature requests, customer complaints, cancellation threats, and non-critical issues.",
        },
    },
    "requires_refund": {
        "type": "noul",
        "instructions": "Determine whether the customer explicitly requests a refund or whether the situation warrants a refund investigation.",
        "criteria": {
            "true": "Duplicate payments, incorrect charges, unauthorized transactions, or explicit refund requests.",
            "false": "General inquiries, technical issues without payment problems, feature requests, and other non-refund requests.",
        },
    },
    "department": {
        "type": "choice",
        "instructions": "Identify the single most appropriate department to handle this ticket based on the customer's primary issue.",
        "criteria": {
            "Technical Support": "Application bugs, crashes, login problems, and technical failures.",
            "Billing": "Payment issues, duplicate charges, refunds, unauthorized transactions, and invoices.",
            "Account Management": "Account settings, profile changes, and account access.",
            "Sales": "Enterprise pricing, subscriptions, upgrades, and commercial inquiries.",
            "Customer Success": "Customer dissatisfaction, complaints, feature requests, and general feedback.",
        },
    },
    "priority": {
        "type": "score",
        "instructions": "Rate the business priority of resolving this ticket on a scale of 1 to 5, considering financial impact, number of affected users, business disruption, and consequences of delay.",
        "criteria": [
            "1 - Very low: General inquiries, appreciation, and non-actionable feedback.",
            "2 - Low: Minor individual requests with minimal business impact.",
            "3 - Medium: Standard support issues requiring resolution.",
            "4 - High: Significant financial impact, repeated complaints, or substantial customer dissatisfaction.",
            "5 - Critical: Security incidents, fraud, or widespread business disruption.",
        ],
    },
    "customer_sentiment": {
        "type": "score",
        "instructions": "Evaluate the customer's emotional sentiment based only on the tone and language of their message, using a scale of 1 to 5.",
        "criteria": [
            "1 - Very negative: Angry, threatening cancellation, or expressing serious dissatisfaction.",
            "2 - Negative: Frustrated, disappointed, or unhappy.",
            "3 - Neutral: Factual communication without strong emotion.",
            "4 - Positive: Satisfied, appreciative, or friendly.",
            "5 - Very positive: Highly enthusiastic or expressing exceptional satisfaction.",
        ],
    },
}

for ticket in inbox:
    ans = ask(ticket, question)

    is_urgent = ans["is_urgent"]["noul"] > 0.5
    requires_refund = ans["requires_refund"]["noul"] > 0.5
    department = ans["department"]["choice"]
    confidence = ans["department"]["confidence"]
    priority = ans["priority"]["score"]
    customer_sentiment = ans["customer_sentiment"]["score"]

    if confidence < 0.75:
        action = "LOW CONFIDENCE: Send to human review"
    elif is_urgent:
        action = f"URGENT: NOTIFY {department} immediately"
    elif requires_refund:
        action = "Add to the refund queue"
    else:
        action = f"Normal queue for {department}"

    print(f"\n{ticket['id']}: {ticket['subject']}")
    print(
        f"  department={department} ({confidence:.0%}), "
        f"urgent={is_urgent}, refund={requires_refund}"
    )
    print(f"  priority={priority:.2f}, sentiment={customer_sentiment:.2f}")
    print(f"  -> {action}")
