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
    # Collect form data
    customer_name = request.form['customer_name']
    customer_address = request.form['customer_address']
    customer_email = request.form['customer_email']
    
    items = []
    # Assuming the form allows multiple items (could be dynamically added in JS or just a few fields in HTML)
    for i in range(1, 4):  # Example with 3 items, modify according to form structure
        description = request.form.get(f'description_{i}')
        quantity = request.form.get(f'quantity_{i}')
        unit_price = request.form.get(f'unit_price_{i}')
        if description and quantity and unit_price:
            items.append(InvoiceItem(description, int(quantity), float(unit_price)))

    received_amount = float(request.form['received_amount'])

    # Create Customer and Invoice instances
    customer = Customer(customer_name, customer_address, customer_email)
    invoice = Invoice(customer, items)

    # Generate the PDF in memory using io.BytesIO
    pdf_output = io.BytesIO()
    balance_due = invoice.total_amount() - received_amount
    logo_path = "static/Fayina_Couture_Logo_2-removebg-preview.png" 
    
    # Call the function to generate the PDF
    generate_invoice_pdf(invoice, pdf_output, logo_path, received_amount, balance_due)

    # Seek to the beginning of the BytesIO buffer
    pdf_output.seek(0)

    # Send the PDF file as an attachment
    return send_file(pdf_output, as_attachment=True, download_name=f'{invoice.invoice_number}.pdf', mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
