from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="CentrAlign Mock Company App")

# Add CORS middleware to allow the Next.js frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated company invoice data
INVOICES = [
    {"id": "INV-100", "vendor": "Company A", "amount": "$500.00", "due_date": "2026-10-10"},
    {"id": "INV-101", "vendor": "Company X", "amount": "$1,250.00", "due_date": "2026-10-15"},
    {"id": "INV-102", "vendor": "Company Y", "amount": "$300.00", "due_date": "2026-11-01"}
]

internal_db = {}
submission_attempts = 0

class InvoiceEntry(BaseModel):
    vendor: str
    amount: str
    due_date: str

@app.get("/invoices")
def get_invoices():
    return {"status": "success", "data": INVOICES}

@app.post("/internal-system")
def submit_invoice(entry: InvoiceEntry):
    global submission_attempts
    submission_attempts += 1
    
    if submission_attempts == 1:
        raise HTTPException(
            status_code=500, 
            detail="Database lock timeout. Please try again."
        )
        
    record_id = f"REC-{len(internal_db) + 1}"
    internal_db[record_id] = entry.model_dump()
    
    return {
        "status": "success", 
        "record_id": record_id, 
        "message": "Invoice processed and stored successfully."
    }

@app.get("/internal-system")
def verify_system_state():
    return {"status": "success", "data": internal_db}

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel

# app = FastAPI(title="CentrAlign Mock Company App")

# # Simulated company invoice data
# INVOICES = [
#     {"id": "INV-100", "vendor": "Company A", "amount": "$500.00", "due_date": "2026-10-10"},
#     {"id": "INV-101", "vendor": "Company X", "amount": "$1,250.00", "due_date": "2026-10-15"},
#     {"id": "INV-102", "vendor": "Company Y", "amount": "$300.00", "due_date": "2026-11-01"}
# ]

# # In-memory database for the internal system
# internal_db = {}
# submission_attempts = 0

# class InvoiceEntry(BaseModel):
#     vendor: str
#     amount: str
#     due_date: str

# @app.get("/invoices")
# def get_invoices():
#     """Returns the list of available invoices."""
#     return {"status": "success", "data": INVOICES}

# @app.post("/internal-system")
# def submit_invoice(entry: InvoiceEntry):
#     """
#     Accepts invoice data. 
#     Intentionally fails on the first attempt to test agent reliability.
#     """
#     global submission_attempts
#     submission_attempts += 1
    
#     if submission_attempts == 1:
#         raise HTTPException(
#             status_code=500, 
#             detail="Database lock timeout. Please try again."
#         )
        
#     record_id = f"REC-{len(internal_db) + 1}"
#     internal_db[record_id] = entry.model_dump()
    
#     return {
#         "status": "success", 
#         "record_id": record_id, 
#         "message": "Invoice processed and stored successfully."
#     }

# @app.get("/internal-system")
# def verify_system_state():
#     """Returns the current state of the internal system for verification."""
#     return {"status": "success", "data": internal_db}