import os
import random
import time
from .data import PASSENGER_DATA # Import PASSENGER_DATA from data.py

# Directory to store dummy PDFs
PDF_DIR = 'invoices'
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

def simulate_airline_portal_download(passenger_id, booking_ref, invoice_id):
    """
    Simulates downloading a PDF from an airline portal.
    - Randomly succeeds or fails for demonstration.
    - On success, creates a dummy PDF file.
    """
    time.sleep(random.uniform(1, 3)) # Simulate network delay

    # 1 in 5 chance of failure or not found
    if random.random() < 0.2:
        return {"status": "NotFound", "message": "Invoice not found on portal."}, None
    elif random.random() < 0.1: # A very small chance of an error
        return {"status": "Error", "message": "Portal internal error."}, None

    # Simulate successful PDF creation
    pdf_filename = f"invoice_{invoice_id}.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_filename)

    # Create a dummy PDF content (actual PDF generation would be more complex)
    dummy_pdf_content = f"""
    %PDF-1.4
    1 0 obj <</Type/Catalog/Pages 2 0 R>> endobj
    2 0 obj <</Type/Pages/Count 1/Kids[3 0 R]>> endobj
    3 0 obj <</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<<>>>> endobj
    4 0 obj <</Length 50>>
    stream
    BT
    /F1 24 Tf
    100 700 Td
    ({invoice_id}) Tj
    100 650 Td
    (Date: 2024-08-28) Tj
    100 600 Td
    (Airline: Dummy Airlines) Tj
    100 550 Td
    (Amount: 1234.56 INR) Tj
    100 500 Td
    (GSTIN: 27ABCDE1234F1Z1) Tj
    ET
    endstream
    endobj
    xref
    0 5
    0000000000 65535 f
    0000000009 00000 n
    0000000056 00000 n
    0000000114 00000 n
    0000000282 00000 n
    trailer
    <</Size 5/Root 1 0 R>>
    startxref
    384
    %%EOF
    """.encode('latin-1')

    try:
        with open(pdf_path, 'wb') as f:
            f.write(dummy_pdf_content)
        return {"status": "Success", "message": "Invoice downloaded successfully."}, pdf_path
    except IOError as e:
        return {"status": "Error", "message": f"Failed to save PDF: {str(e)}"}, None


def parse_pdf_invoice(pdf_path):
    """
    Mocks PDF parsing to extract key details.
    In a real application, you'd use a library like PyMuPDF or PyPDF2
    and implement robust regex or ML-based extraction.
    """
    time.sleep(random.uniform(0.5, 2)) # Simulate parsing time

    if not os.path.exists(pdf_path):
        return {"status": "Error", "message": "PDF file not found for parsing."}, None

    try:
        with open(pdf_path, 'rb') as f:
            content = f.read().decode('latin-1') # Decode dummy PDF content

        # Simple regex-like extraction from our dummy content
        invoice_num = next((line.strip() for line in content.splitlines() if "INV" in line), "N/A").replace("(", "").replace(")", "").strip()
        date = next((line.split("Date: ")[1].split(" ")[0].strip() for line in content.splitlines() if "Date:" in line), "N/A")
        airline = next((line.split("Airline: ")[1].split(" ")[0].strip() for line in content.splitlines() if "Airline:" in line), "N/A")
        amount = next((line.split("Amount: ")[1].split(" ")[0].strip() for line in content.splitlines() if "Amount:" in line), "N/A")
        gstin = next((line.split("GSTIN: ")[1].split(" ")[0].strip() for line in content.splitlines() if "GSTIN:" in line), "N/A")

        # Simulate a parsing failure for specific invoice (e.g., P003)
        if "INV2024003" in invoice_num and random.random() < 0.7: # 70% chance of parsing error for P003
            return {"status": "Error", "message": "Simulated parsing error for this invoice."}, None

        return {
            "status": "Success",
            "invoiceNumber": invoice_num,
            "date": date,
            "airline": airline,
            "amount": float(amount.replace(" INR", "")),
            "gstin": gstin if gstin != "N/A" else None
        }, None
    except Exception as e:
        return {"status": "Error", "message": f"Failed to parse PDF: {str(e)}"}, None

def get_all_passengers():
    return PASSENGER_DATA

def update_passenger_data(passenger_id, new_data):
    """Updates a passenger's data in the in-memory store."""
    for i, p in enumerate(PASSENGER_DATA):
        if p['id'] == passenger_id:
            PASSENGER_DATA[i] = {**p, **new_data}
            return PASSENGER_DATA[i]
    return None

def get_parsed_invoices():
    return [p for p in PASSENGER_DATA if p['parseStatus'] == "Success" and p['invoiceData']]

def get_invoices_summary():
    summary = {}
    for p in PASSENGER_DATA:
        if p['parseStatus'] == "Success" and p['invoiceData'] and p['invoiceData'].get('airline') and p['invoiceData'].get('amount') is not None:
            airline = p['invoiceData']['airline']
            amount = p['invoiceData']['amount']
            if airline not in summary:
                summary[airline] = {"totalAmount": 0, "count": 0}
            summary[airline]['totalAmount'] += amount
            summary[airline]['count'] += 1
    return summary

def get_high_value_invoices(threshold=1000.0):
    high_value_invoices = [
        p for p in PASSENGER_DATA
        if p['parseStatus'] == "Success" and p['invoiceData'] and p['invoiceData'].get('amount', 0) > threshold
    ]
    return high_value_invoices
