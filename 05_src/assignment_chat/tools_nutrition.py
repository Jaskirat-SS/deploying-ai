from langchain.tools import tool
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('.secrets')

CALORIE_NINJAS_API_KEY = os.getenv("CALORIE_NINJAS_API_KEY")

@tool
def get_nutrition_facts(food_item: str) -> str:
    """
    Returns the nutritional content of a given food item using the CalorieNinjas API.
    The response includes calories, carbohydrates, protein, fat, and fiber,
    rephrased into a natural, human-readable sentence.
    """
    url = "https://api.calorieninjas.com/v1/nutrition"
    headers = {
        "X-Api-Key": CALORIE_NINJAS_API_KEY
    }
    params = {
        "query": food_item
    }

    response = requests.get(url, headers=headers, params=params)
    resp_dict = json.loads(response.text)
    items = resp_dict.get("items", [])

    if not items:
        return f"Sorry, I couldn't find any nutritional information for '{food_item}'. Please try a different food item."

    # Aggregate totals in case multiple items are returned (e.g. "100g chicken and rice")
    total_calories = sum(item.get("calories", 0) for item in items)
    total_carbs = sum(item.get("carbohydrates_total_g", 0) for item in items)
    total_protein = sum(item.get("protein_g", 0) for item in items)
    total_fat = sum(item.get("fat_total_g", 0) for item in items)
    total_fiber = sum(item.get("fiber_g", 0) for item in items)

    # Transform structured JSON into a natural language response
    result = (
        f"{food_item.capitalize()} contains roughly "
        f"{round(total_calories)} calories, "
        f"{round(total_carbs, 1)}g of carbohydrates, "
        f"{round(total_protein, 1)}g of protein, "
        f"{round(total_fat, 1)}g of fat, and "
        f"{round(total_fiber, 1)}g of fiber."
    )

    return result