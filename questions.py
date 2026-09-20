
#Bellow are five test questions the system can answer from the city_guides corpus."

QUESTIONS = [
    {
        "question": "When is the best time to book railway tickets at a cheaper-than-normal rate?",
        "expects": (
            "The best time to purchase cheaper tickets is the day before "
            "or when booking a week ahead."
        ),
    },
    {
        "question": "Which cities have free parking?",
        "expects": (
            "Kestreford's lower car park area is the only city with "
            "free parking."
        ),
    },
    {
        "question": (
            "What are some fun things visitors can do while in "
            "Kestreford and Marchwood?"
        ),
        "expects": (
            "The Sunday morning market square is the main event in Kestreford "
            "and has run continuously since the 1400s. In Marchwood, the city "
            "museum is an excellent visitor attraction. The canal walk from "
            "Northgate to the old lock is recommended by residents when asked "
            "by visitors."
        ),
    },
    {
        "question": "Where is the hospital located?",
        "expects": (
            "The nearest hospital is in Brightwater. It has a minor injuries "
            "unit locally with limited hours."
        ),
    },
    {
        "question": (
            "What is the best means of transportation with the shortest "
            "travel time from Brightwater to Givens Mill?"
        ),
        "expects": (
            "The shortest route from Brightwater to Givens Mill takes "
            "20 minutes by car."
        ),
    },
]

# Questions from a different world entirely. Your gate should refuse all five.
#
# There are five of these because criterion 3 in criteria.md names a target of
# "at least 4 of 5" — you need five things to try before you can report 4 of 5.
# `run_eval.py` runs these through retrieval and the gate on every eval and
# records what happened, so criterion 3 has evidence in the run log alongside
# the others. They cost no model calls: a refusal never reaches the model.

OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
    "What is the recommended dosage of ibuprofen for a headache?",
    "How do I write a for loop in Rust?",
]


def answered() -> list[dict]:
    """The questions you've actually filled in."""
    return [q for q in QUESTIONS if q.get("question", "").strip()]
