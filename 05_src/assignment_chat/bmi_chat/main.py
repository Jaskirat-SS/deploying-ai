from openai import OpenAI
from dotenv import load_dotenv
from bmi_chat.prompts import return_instructions_root
import json
import requests
from utils.logger import get_logger
import os


_logs = get_logger(__name__)

load_dotenv(".env")
load_dotenv(".secrets")


client = OpenAI()

open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4")

tools = [
    {
        "type": "function",
        "name": "calculate_bmi",
        "description": "This tool calculates the Body Mass Index (BMI) given the user's height and weight, and returns the BMI value along with the category and diet recommendations.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "weight": {
                    "type": "number",
                    "description": "The weight of the user. Can be in kilograms (kg) or pounds (lbs).",
                },
                "height": {
                    "type": "number",
                    "description": "The height of the user. Can be in meters (m) or inches (in).",
                },
                "unit_system": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "description": "The unit system being used. 'metric' for kg and meters, 'imperial' for lbs and inches.",
                }
            },
            "required": ["weight", "height", "unit_system"],
            "additionalProperties": False
        },
    },
]


def calculate_bmi(weight: float, height: float, unit_system: str) -> str:
    """
    Calculates BMI based on the provided weight, height, and unit system.
    - Metric: BMI = weight(kg) / height(m)^2
    - Imperial: BMI = 703 * weight(lbs) / height(inches)^2
    Returns BMI value, category, and diet recommendations.
    """

    if unit_system == "metric":
        bmi = weight / (height ** 2)
    elif unit_system == "imperial":
        bmi = 703 * weight / (height ** 2)
    else:
        return "Invalid unit system provided. Please specify 'metric' or 'imperial'."

    bmi = round(bmi, 2)

    if bmi < 18.5:
        category = "Underweight"
        diet_recommendations = (
            "You are underweight. Consider a calorie-surplus diet rich in proteins, healthy fats, "
            "and complex carbohydrates. Include foods like nuts, whole grains, lean meats, dairy, "
            "and avocados. Eating more frequent meals throughout the day can also help."
        )
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
        diet_recommendations = (
            "Great job! You have a healthy weight. Maintain a balanced diet with a mix of fruits, "
            "vegetables, lean proteins, whole grains, and healthy fats. Stay hydrated and keep up "
            "with regular physical activity."
        )
    elif 25 <= bmi < 30:
        category = "Overweight"
        diet_recommendations = (
            "You are overweight. Consider a calorie-controlled diet focusing on whole foods. "
            "Reduce processed sugar and fat intake, increase fiber-rich foods, lean proteins, "
            "and vegetables, and cut back on refined carbohydrates. Regular exercise is also recommended."
        )
    else:
        category = "Obese"
        diet_recommendations = (
            "Your BMI indicates obesity. A structured, low-calorie, nutrient-dense diet is recommended. "
            "Focus on vegetables, lean proteins, and water while reducing processed foods and sugary drinks. "
            "It is strongly advised to consult a healthcare professional or registered nutritionist "
            "for a personalized plan."
        )

    result = (
        f"BMI Result:\n"
        f"  - BMI Value: {bmi}\n"
        f"  - Category: {category}\n"
        f"  - Diet Recommendations: {diet_recommendations}\n\n"
        f"Disclaimer: BMI is a general health indicator and is not a substitute for professional medical advice."
    )

    return result


def sanitize_history(history: list[dict]) -> list[dict]:
    clean_history = []
    for msg in history:
        clean_history.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
    return clean_history


def bmi_chat(message: str, history: list[dict] = []) -> str:
    _logs.info(f'User message: {message}')

    instructions = return_instructions_root()

    user_msg = {
        "role": "user",
        "content": message
    }

    conversation_input = sanitize_history(history) + [user_msg]

    response = client.responses.create(
        model=open_ai_model,
        instructions=instructions,
        input=conversation_input,
        tools=tools,
    )

    conversation_input += response.output

    # Handle function calls if any
    for item in response.output:
        if item.type == "function_call":
            if item.name == "calculate_bmi":
                args = json.loads(item.arguments)
                _logs.info(f'Function call args: {args}')

                # Call the BMI calculation function
                bmi_result = calculate_bmi(**args)

                # Add function call result to conversation
                func_call_output = {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "bmi_result": bmi_result
                    })
                }

                _logs.debug(f"Function call output: {func_call_output}")

                conversation_input = conversation_input + [func_call_output]

                # Make second API call with function result
                response = client.responses.create(
                    model=open_ai_model,
                    instructions=instructions,
                    tools=tools,
                    input=conversation_input
                )
                break

    return response.output_text
