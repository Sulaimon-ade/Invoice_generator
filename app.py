from flask import Flask, render_template, request, send_file, redirect, url_for
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

# Import your classes for Customer, Invoice, etc.
# You can keep these classes in a separate file for better structure and import them here.
from invoice_generator import Customer, Invoice, InvoiceItem, generate_invoice_pdf

app = Flask(__name__)

# Home page with form to input invoice details
@app.route('/')
def index():
    return render_template('index.html')  # The form for inputting customer and invoice data

# Route to generate the invoice PDF
@app.route('/generate', methods=['POST'])
def generate_invoice():
    # Collect form data for customer
    customer_name = request.form['customer_name']
    customer_address = request.form['customer_address']
    customer_email = request.form['customer_email']

    # Create a Customer instance
    customer = Customer(customer_name, customer_address, customer_email)
    
    # Collect form data for multiple items
    descriptions = request.form.getlist('description[]')
    quantities = request.form.getlist('quantity[]')
    unit_prices = request.form.getlist('unit_price[]')
    
    # Create a list of InvoiceItem objects
    items = []
    for description, quantity, unit_price in zip(descriptions, quantities, unit_prices):
        items.append(InvoiceItem(description, int(quantity), float(unit_price)))

    # Received amount
    received_amount = float(request.form['received_amount'])

    # Create an Invoice instance
    invoice = Invoice(customer, items)
    
    # Calculate balance due
    balance_due = invoice.total_amount() - received_amount

    # Generate the PDF in memory using io.BytesIO
    pdf_output = io.BytesIO()
    logo_path = "static/Fayina_Couture_Logo_2-removebg-preview.png"
    
    # Generate the PDF using your existing function
    generate_invoice_pdf(invoice, pdf_output, logo_path, received_amount, balance_due)

    # Send the PDF as a downloadable file
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name=f'{invoice.invoice_number}.pdf', mimetype='application/pdf')
if __name__ == "__main__":
    app.run(debug=True)
