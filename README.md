# AutoTask: Autonomous AI Task Worker (Playwright + Next.js Edition)

An autonomous AI task worker prototype built for the CentrAlign AI Engineering Intern evaluation. The system accepts natural language instructions, visually navigates a simulated company frontend using a headless browser, sanitizes data through autonomous error recovery, requests human approval before committing data, and verifies persistence via a backend API state read-back.

## Architecture Overview

The system runs a LangGraph ReAct (Reasoning + Acting) loop against a local full-stack environment.

1. **Frontend (Next.js/Tailwind):** A local web environment serving an asynchronous invoice data table and a strict-typed internal submission form (`<input type="number">`).
2. **Backend (FastAPI):** A mock internal database that intentionally injects a `500 Database lock timeout` on the first submission to test agent reliability.


3. **Agent (LangGraph + Groq):** Orchestrates the `Plan -> Scrape (Playwright) -> Sanitize -> Request Approval -> Submit (Playwright) -> Recover -> Verify` workflow.

## Key Capabilities Demonstrated

* **Browser Automation & Computer Use:** Uses Playwright to physically navigate the DOM, await asynchronous React hydration (`.invoice-row`), extract table data, and type into form fields.


* **Autonomous Error Recovery & Data Sanitization:** If the agent attempts to input a raw string (e.g., `"$1,250.00"`) into a strict `type="number"` field, it catches the Playwright DOM error, autonomously infers the need to strip special characters, and retries with `"1250.00"`.


* **Human Approval Systems:** Execution pauses automatically before any mutating action (`submit_to_internal_system`). The terminal displays the exact payload and requires a manual `y/n` input to proceed safely.


* **Failure Detection:** Detects backend `500` status errors reflected in the frontend UI banner and automatically re-executes the form submission.


* **Explicit Outcome Verification:** Instead of assuming a successful UI click means the task is done, the agent makes a direct API call to `verify_system_state` to perform a diff against the backend database before reporting completion.



## Setup & Execution

### 1. Prerequisites

* Python 3.10+
* Node.js & npm
* Groq API Key (`openai/gpt-oss-20b` model)

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Start the Backend API (FastAPI)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn mock_server:app --reload --port 8000
```

### 4. Start the Frontend (Next.js)

In a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

### 5. Run the Agent

In a final terminal window (with the venv activated):

```bash
python agent.py
```

*Note: The agent will pause in the terminal to request your approval before submitting data to the form.*

## Technical Decisions & Assumptions

* **Model Selection:** `openai/gpt-oss-20b` was selected via Groq for its high speed and strict adherence to function-calling schemas. Temperature is set to `0` to prevent hallucinated tool arguments.
* **Verification Strategy:** Form submission tools and verification tools are decoupled. The agent is explicitly prompted to separate the act of clicking "Submit" from the act of verifying the final database state.
* **Headless Execution:** Playwright is configured `headless=True` for faster execution, relying on terminal logs to surface DOM observations.