from langgraph.graph import StateGraph, MessagesState, START
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
from assignment_chat.prompts import return_instructions
from assignment_chat.tools_bmi import calculate_bmi
from assignment_chat.tools_nutrition import get_nutrition_facts
from assignment_chat.tools_pdfsummary import search_canada_food_guide
from utils.logger import get_logger

_logs = get_logger(__name__)

load_dotenv(".env")
load_dotenv(".secrets")

chat_agent = ChatOpenAI(
    model="gpt-4o-mini",  # ← hardcoded correctly now, not wrapped in os.getenv()
    base_url="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    api_key="any_value",
    default_headers={"x-api-key": os.getenv("API_GATEWAY_KEY")}
)

tools = [calculate_bmi, get_nutrition_facts, search_canada_food_guide]

instructions = return_instructions()

def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    response = chat_agent.bind_tools(tools).invoke(
        [SystemMessage(content=instructions)] + state["messages"]
    )
    return {
        "messages": [response]
    }

def get_graph():
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    graph = builder.compile()
    return graph