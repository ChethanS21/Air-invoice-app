# backend/main.py

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from backend.services import (
    simulate_airline_portal_download,
    parse_pdf_invoice,
    get_all_passengers,
    update_passenger_data,
    get_parsed_invoices,
    get_invoices_summary,
    get_high_value_invoices,
    PDF_DIR
)
from backend.data import PASSENGER_DATA # Import PASSENGER_DATA for direct access for finds

app = Flask(__name__)
CORS(app) # Enable CORS for frontend to access

# --- API Endpoints ---

@app.route('/api/passengers', methods=['GET'])
def get_passengers():
    """Retrieves the list of all passenger records."""
    return jsonify(get_all_passengers())

@app.route('/api/passengers/<passenger_id>/download', methods=['POST'])
def download_invoice():
    """Triggers invoice download for a specific passenger."""
    passenger_id = request.view_args['passenger_id'] # Correctly get passenger_id from view_args
    passenger = next((p for p in PASSENGER_DATA if p['id'] == passenger_id), None)
    if not passenger:
        return jsonify({"message": "Passenger not found"}), 404

    result, pdf_path = simulate_airline_portal_download(
        passenger_id, passenger['bookingRef'], passenger['invoiceId']
    )

    new_data = {
        'downloadStatus': result['status'],
        'pdfPath': pdf_path if result['status'] == "Success" else None
    }
    updated_passenger = update_passenger_data(passenger_id, new_data)

    if result['status'] == "Error":
        return jsonify({"message": result['message'], "status": result['status']}), 500
    elif result['status'] == "NotFound":
        return jsonify({"message": result['message'], "status": result['status']}), 404
    return jsonify(updated_passenger)

@app.route('/api/passengers/<passenger_id>/parse', methods=['POST'])
def parse_invoice():
    """Triggers invoice parsing for a specific passenger."""
    passenger_id = request.view_args['passenger_id'] # Correctly get passenger_id from view_args
    passenger = next((p for p in PASSENGER_DATA if p['id'] == passenger_id), None)
    if not passenger:
        return jsonify({"message": "Passenger not found"}), 404

    if passenger['downloadStatus'] != "Success" or not passenger['pdfPath']:
        update_passenger_data(passenger_id, {'parseStatus': "Error"})
        return jsonify({"message": "PDF not downloaded or path missing.", "status": "PreconditionFailed"}), 412

    parsed_data, error_msg = parse_pdf_invoice(passenger['pdfPath'])

    if parsed_data['status'] == "Success":
        new_data = {
            'parseStatus': "Success",
            'invoiceData': {k: v for k, v in parsed_data.items() if k != "status"}
        }
        updated_passenger = update_passenger_data(passenger_id, new_data)
        return jsonify(updated_passenger)
    else:
        new_data = {
            'parseStatus': "Error",
            'invoiceData': {"error": parsed_data.get("message", "Unknown parsing error")}
        }
        updated_passenger = update_passenger_data(passenger_id, new_data)
        return jsonify({"message": parsed_data.get("message", "Unknown parsing error"), "status": "ParsingError"}), 500

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    """Retrieves a list of all parsed invoices."""
    return jsonify(get_parsed_invoices())

@app.route('/api/invoices/summary', methods=['GET'])
def get_summary_endpoint():
    """Provides a summary view (e.g., airline-wise totals)."""
    return jsonify(get_invoices_summary())

@app.route('/api/invoices/high-value', methods=['GET'])
def get_high_value_endpoint():
    """Identifies high-value invoices above a certain threshold (default 1000)."""
    threshold = request.args.get('threshold', type=float, default=1000.0)
    return jsonify(get_high_value_invoices(threshold))

@app.route('/invoices/<filename>', methods=['GET'])
def serve_pdf(filename):
    """Serves the dummy PDF files."""
    return send_from_directory(PDF_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

