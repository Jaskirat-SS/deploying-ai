import gradio as gr
from bmi_chat.main import bmi_chat
from dotenv import load_dotenv
from utils.logger import get_logger

_logs = get_logger(__name__)

load_dotenv('.env')
load_dotenv('.secrets')


def chat_handler(message: str, history: list[dict]) -> str:
    _logs.debug(f"History: {history}")

    formatted_history = []
    for msg in history:
        if msg['role'] == 'user':
            formatted_history.append({"role": "user", "content": msg['content']})
        elif msg['role'] == 'assistant':
            formatted_history.append({"role": "assistant", "content": msg['content']})

    return bmi_chat(message=message, history=formatted_history)


chat = gr.ChatInterface(
    fn=chat_handler,
    type="messages",
    title="BMI Calculator & Diet Recommendation Assistant",
    description=(
        "Welcome! Provide your **height** and **weight** to calculate your BMI "
        "and receive personalized diet recommendations."
    ),
    examples=[
        ["My height is 1.75m and weight is 70kg."],
        ["I am 5ft 10in tall and weigh 180 pounds."],
    ]
)

if __name__ == "__main__":
    _logs.info('Starting BMI Chat App...')
    chat.launch()
