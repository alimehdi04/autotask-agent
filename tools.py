import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

BASE_API_URL = "https://autotask-agent-tzep.onrender.com"
FRONTEND_URL = "https://autotask-agent.vercel.app"

@tool
def fetch_invoices() -> str:
    """Fetches the list of pending invoices by visually scraping the company dashboard."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{FRONTEND_URL}/invoices")
            
            # Wait specifically for the async React data to render into rows
            page.wait_for_selector(".invoice-row", timeout=10000)
            
            # Scrape the DOM
            rows = page.locator(".invoice-row").all()
            data = []
            for row in rows:
                data.append({
                    "id": row.locator("td").nth(0).inner_text(),
                    "vendor": row.locator(".vendor-cell").inner_text(),
                    "amount": row.locator(".amount-cell").inner_text(),
                    "due_date": row.locator(".date-cell").inner_text(),
                })
            
            browser.close()
            return str(data)
    except Exception as e:
        return f"Error fetching invoices via browser: {str(e)}"

@tool
def submit_to_internal_system(vendor: str, amount: str, due_date: str) -> str:
    """
    Submits extracted invoice details by physically typing them into the internal web form.
    Args:
        vendor: The name of the company on the invoice.
        amount: The invoice amount (e.g., '$1,250.00').
        due_date: The date the invoice is due (e.g., '2026-10-15').
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{FRONTEND_URL}/internal-system")
            
            # Physically fill the form
            page.fill("#vendor-input", vendor)
            page.fill("#amount-input", amount)
            page.fill("#date-input", due_date)
            
            # Click the submit button
            page.click("#submit-btn")
            
            # Wait for the UI to update with either success or error message
            page.wait_for_selector("#status-message", state="visible")
            status_text = page.inner_text("#status-message")
            
            browser.close()
            
            # If the UI shows the red error banner, flag it so the agent knows to retry
            if "Error" in status_text:
                return f"Action Failed in UI: {status_text}"
            return status_text
            
    except Exception as e:
        return f"Error submitting invoice via browser: {str(e)}"

@tool
def verify_system_state() -> str:
    """Fetches all records currently saved in the internal database API to verify if a submission was successful."""
    # We leave verification as an API call, as checking the underlying database state 
    # is a more robust verification method than just reading the frontend "success" banner.
    try:
        response = requests.get(f"{BASE_API_URL}/internal-system")
        response.raise_for_status()
        return response.text
    except Exception as e:
         return f"Error verifying system state: {str(e)}"

# Initialize Groq LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=2,
)

# Bind the tools to the LLM
tools = [fetch_invoices, submit_to_internal_system, verify_system_state]
llm_with_tools = llm.bind_tools(tools)