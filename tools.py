import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq

# Load environment variables from .env
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

@tool
def fetch_invoices() -> str:
    """Fetches the list of all available invoices from the company system."""
    try:
        response = requests.get(f"{BASE_URL}/invoices")
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching invoices: {str(e)}"

@tool
def submit_to_internal_system(vendor: str, amount: str, due_date: str) -> str:
    """
    Submits extracted invoice details to the internal system.
    Args:
        vendor: The name of the company on the invoice.
        amount: The invoice amount (e.g., '$1,250.00').
        due_date: The date the invoice is due (e.g., '2026-10-15').
    """
    payload = {"vendor": vendor, "amount": amount, "due_date": due_date}
    try:
        response = requests.post(f"{BASE_URL}/internal-system", json=payload)
        # We explicitly capture non-200 responses as text so the agent can read the error and know to retry
        if response.status_code != 200:
            return f"Action Failed. Status Code {response.status_code}: {response.text}"
        return response.text
    except Exception as e:
        return f"Error submitting invoice: {str(e)}"

@tool
def verify_system_state() -> str:
    """Fetches all records currently saved in the internal system to verify if a submission was successful."""
    try:
        response = requests.get(f"{BASE_URL}/internal-system")
        response.raise_for_status()
        return response.text
    except Exception as e:
         return f"Error verifying system state: {str(e)}"

# Initialize Groq LLM
# We use a 0 temperature for deterministic, highly reliable reasoning
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=2,
)

# Bind the tools to the LLM
tools = [fetch_invoices, submit_to_internal_system, verify_system_state]
llm_with_tools = llm.bind_tools(tools)

# Quick test block (runs only if you execute this file directly)
if __name__ == "__main__":
    print("Testing Groq connection and tool binding...")
    test_msg = llm_with_tools.invoke("What tools do you have access to?")
    print(f"Tool calls requested by LLM: {test_msg.tool_calls}")