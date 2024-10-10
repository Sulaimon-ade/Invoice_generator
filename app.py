from flask import Flask, render_template, request, send_file
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

# Import your classes for Customer, Invoice, etc.
from invoice_generator import Customer, Invoice, InvoiceItem, generate_invoice_pdf

app = Flask(__name__)

# Home page with form to input invoice details
@app.route('/')
def index():
    return render_template('index.html')  # The form for inputting customer and invoice data

# Route to generate the invoice PDF
@app.route('/generate', methods=['POST'])
def generate_invoice():
    # Helper function to remove commas from numbers
    def parse_number(value):
        return float(value.replace(',', ''))

    # Collect form data for customer
    customer_name = request.form['customer_name']
    customer_address = request.form['customer_address'] or "Not Provided"  # Handle empty address
    customer_email = request.form['customer_email'] or "Not Provided"  # Handle empty email

    # Create a Customer instance
    customer = Customer(customer_name, customer_address, customer_email)
    
    # Collect form data for multiple items
    descriptions = request.form.getlist('description[]')
    quantities = [parse_number(q) for q in request.form.getlist('quantity[]')]  # Remove commas
    unit_prices = [parse_number(p) for p in request.form.getlist('unit_price[]')]  # Remove commas
    
    # Create a list of InvoiceItem objects
    items = []
    for description, quantity, unit_price in zip(descriptions, quantities, unit_prices):
        items.append(InvoiceItem(description, int(quantity), float(unit_price)))

    # Get discount and received amount
    discount = parse_number(request.form['discount']) if request.form['discount'] else 0.0
    received_amount = parse_number(request.form['received_amount'])

    # Create an Invoice instance
    invoice = Invoice(customer, items)

    # Apply the discount
    total_amount_before_discount = invoice.total_amount()
    total_amount_after_discount = total_amount_before_discount - discount

    # Ensure total is non-negative after discount
    total_amount_after_discount = max(0, total_amount_after_discount)

    # Calculate balance due
    balance_due = total_amount_after_discount - received_amount

    # Generate the PDF in memory using io.BytesIO
    pdf_output = io.BytesIO()
    logo_path = "static/Fayina_Couture_Logo_2-removebg-preview.png"
    
    # Pass the discount value to the PDF generation function
    generate_invoice_pdf(invoice, pdf_output, logo_path, received_amount, balance_due, discount=discount)

    # Send the PDF as a downloadable file
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name=f'{invoice.invoice_number}.pdf', mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
