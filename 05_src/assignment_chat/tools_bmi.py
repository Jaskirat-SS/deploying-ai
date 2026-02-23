from langchain.tools import tool
from utils.logger import get_logger

_logs = get_logger(__name__)


@tool
def calculate_bmi(weight: float, height: float, unit_system: str) -> str:
    """
    Calculates the Body Mass Index (BMI) for a user given their weight, height, and unit system.
    
    Accepted values for unit_system are: 'metric' or 'imperial'.
    For metric: weight in kilograms (kg), height in meters (m).
    For imperial: weight in pounds (lbs), height in inches (in).
    
    Returns the BMI value, category, and diet recommendations in a natural language response.
    """
    _logs.debug(f'Calculating BMI for weight={weight}, height={height}, unit_system={unit_system}')

    # Calculate BMI based on unit system
    if unit_system.lower() == "metric":
        bmi = weight / (height ** 2)
    elif unit_system.lower() == "imperial":
        bmi = 703 * weight / (height ** 2)
    else:
        return "Invalid unit system. Please specify 'metric' or 'imperial'."

    bmi = round(bmi, 2)
    _logs.debug(f'Calculated BMI: {bmi}')

    # Determine BMI category and diet recommendations
    if bmi < 18.5:
        category = "Underweight"
        diet_recommendations = (
            "Consider a calorie-surplus diet rich in proteins, healthy fats, and complex carbohydrates. "
            "Include foods like nuts, whole grains, lean meats, dairy, and avocados. "
            "Eating more frequent meals throughout the day can also help."
        )
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
        diet_recommendations = (
            "Maintain a balanced diet with a mix of fruits, vegetables, lean proteins, "
            "whole grains, and healthy fats. Stay hydrated and keep up with regular physical activity."
        )
    elif 25 <= bmi < 30:
        category = "Overweight"
        diet_recommendations = (
            "Consider a calorie-controlled diet focusing on whole foods. "
            "Reduce processed sugar and fat intake, increase fiber-rich foods, lean proteins, "
            "and vegetables, and cut back on refined carbohydrates. Regular exercise is also recommended."
        )
    else:
        category = "Obese"
        diet_recommendations = (
            "A structured, low-calorie, nutrient-dense diet is recommended. "
            "Focus on vegetables, lean proteins, and water while reducing processed foods and sugary drinks. "
            "It is strongly advised to consult a healthcare professional or registered nutritionist "
            "for a personalized plan."
        )

    result = (
        f"Based on the details provided, your BMI is {bmi}, which falls in the '{category}' category.\n\n"
        f"Diet Recommendations: {diet_recommendations}\n\n"
        f"Disclaimer: BMI is a general health indicator and is not a substitute for professional medical advice."
    )

    _logs.debug(f'BMI result: {result}')
    return result