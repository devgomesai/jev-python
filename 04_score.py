""" score: rate something on a scale you define """
from jev import ask

candidates = [
    "Candidate has 3 years of Python experience, strong SQL skills, AWS certification, and has built production ML applications.",
    "Candidate has 6 months of Python experience, knows basic SQL, and has completed two academic projects.",
    "Candidate has 5 years of Java experience, Spring Boot expertise, and experience building microservices.",
    "Candidate has no professional experience but has completed a machine learning course and knows Python basics.",
    "Candidate has 4 years of Python, FastAPI, PostgreSQL, Docker, and AWS experience."
]

question = {
    "candidate_score": {
        "type": "score",
        "instructions": "Evaluate how well the candidate matches a Python AI Backend Developer role.",
        "criteria": [
            "Poor: No relevant programming experience or skills.",
            "Basic: Fundamental Python knowledge with academic projects.",
            "Average: Some practical Python experience and basic backend knowledge.",
            "Good: Strong Python, backend development and database skills.",
            "Excellent: Extensive Python backend experience, cloud skills and production AI applications."
        ]
    }
}

def main() -> None:
    for candidate in candidates:
        ans = ask(state=candidate, questions=question)
        candidate_score = ans["candidate_score"]

        level = round(candidate_score["score"])
        label = candidate_score["legend"][str(level)]

        print(candidate)
        print(f" score {candidate_score['score']:.2f} -> {label} ({candidate_score['confidence']:.0%} confident)")


if __name__ == "__main__":
    main()
