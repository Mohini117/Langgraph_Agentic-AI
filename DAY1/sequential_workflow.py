from typing import Literal, TypedDict, cast

from langgraph.graph import END, START, StateGraph


ActivityLevel = Literal[
    "sedentary",
    "lightly_active",
    "moderately_active",
    "very_active",
    "extra_active",
]


class CalorieState(TypedDict, total=False):
    gender: Literal["male", "female"]
    weight: float
    height: float
    age: int
    activity_level: ActivityLevel
    bmr: float
    tdee: float


def calculate_bmr(state: CalorieState) -> CalorieState:
    gender = state["gender"].strip().lower()
    weight = state["weight"]
    height = state["height"]
    age = state["age"]

    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        raise ValueError("gender must be 'male' or 'female'")

    return {"bmr": round(bmr, 2)}


def calculate_tdee(state: CalorieState) -> CalorieState:
    multipliers: dict[ActivityLevel, float] = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9,
    }

    activity_level = state["activity_level"].strip().lower()
    if activity_level not in multipliers:
        raise ValueError(
            "activity_level must be one of: sedentary, lightly_active, "
            "moderately_active, very_active, extra_active"
        )

    activity_level_key = cast(ActivityLevel, activity_level)
    tdee = state["bmr"] * multipliers[activity_level_key]
    return {"tdee": round(tdee, 2)}


graph = StateGraph(CalorieState)
graph.add_node("calculate_bmr", calculate_bmr)
graph.add_node("calculate_tdee", calculate_tdee)
graph.add_edge(START, "calculate_bmr")
graph.add_edge("calculate_bmr", "calculate_tdee")
graph.add_edge("calculate_tdee", END)

workflow = graph.compile()


if __name__ == "__main__":
    initial_state: CalorieState = {
        "gender": "female",
        "weight": 80,
        "height": 173,
        "age": 30,
        "activity_level": "lightly_active",
    }
    final_state = workflow.invoke(initial_state)
    print(final_state)
