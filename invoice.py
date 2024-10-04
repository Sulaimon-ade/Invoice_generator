import json
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer

# Constants
CUSTOMERS_FILE = 'customers.json'
INVOICES_FILE = 'invoices.json'
RECEIVED_AMOUNT = 50000  # Example received amount, modify as needed

# Model for a Customer
class Customer:
    def __init__(self, name, address, email):
        self.name = name
        self.address = address
        self.email = email

    def to_dict(self):
        return {"name": self.name, "address": self.address, "email": self.email}

# Model for an Invoice Item
class InvoiceItem:
    def __init__(self, description, quantity, unit_price):
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price

    def total_price(self):
        return self.quantity * self.unit_price

    def to_dict(self):
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price()
        }

# Model for an Invoice
class Invoice:
    def __init__(self, customer, items, tax_rate=0.1):
        self.customer = customer
        self.items = items
        self.tax_rate = tax_rate
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.invoice_number = f"INV-{int(datetime.now().timestamp())}"

    def total_before_tax(self):
        return sum(item.total_price() for item in self.items)

    def tax_amount(self):
        return self.total_before_tax() * self.tax_rate

    def total_amount(self):
        return self.total_before_tax() + self.tax_amount()

    def to_dict(self):
        return {
            "invoice_number": self.invoice_number,
            "customer": self.customer.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "tax_rate": self.tax_rate,
            "total_before_tax": self.total_before_tax(),
            "tax_amount": self.tax_amount(),
            "total_amount": self.total_amount(),
            "date": self.date
        }

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter

# Function to draw the watermark/logo
def draw_watermark(canvas, logo_path, width, height):
    canvas.saveState()
    # Make the logo light and transparent
    canvas.setFillGray(0.9, 0.5)  # 0.9 makes it light, 0.5 is transparency
    # Position logo (x, y, width, height) on the page
    canvas.drawImage(logo_path, x=0, y=800 // 2, width=300, height=300, mask='auto')
    canvas.restoreState()

# Overriding the canvas object to include the watermark
class WatermarkedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        self.logo_path = kwargs.pop('logo_path', None)
        super().__init__(*args, **kwargs)

    def showPage(self):
        # Add watermark (logo) on every page
        if self.logo_path:
            draw_watermark(self, self.logo_path, *A4)
        super().showPage()

# Function to generate PDF invoice with watermark
def generate_invoice_pdf(invoice, filename, logo_path=None, received_amount=0, balance_due=0):
    pdf = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    # Table Styles (reusable)
    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
    ])
    
    # Invoice header section
    invoice_header = [["INVOICE", f"Invoice #{invoice.invoice_number}"],
                      ["Date:", invoice.date],
                      ["Fayina Luxury Couture", "fayinaluxurycouture@yahoo.com"],
                      ["Phone:", "+2349032837162"]]
    
    table_header = Table(invoice_header)
    table_header.setStyle(header_style)
    elements.append(table_header)
    elements.append(Spacer(1, 0.2 * inch))

    # Customer and Payment Details
    customer_payment_details = [["Bill to:", invoice.customer.name], ["Payment to:", "Fayina Luxury Couture Ltd, GTB Bank Plc, 0214413459"]]
    table_customer_payment = Table(customer_payment_details)
    table_customer_payment.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTSIZE', (0, 0), (-1, -1), 12)]))
    elements.append(table_customer_payment)
    elements.append(Spacer(1, 0.2 * inch))

    # Line Items Section
    items_data = [["# Item", "Qty", "Unit Price", "Amount"]]
    for idx, item in enumerate(invoice.items, start=1):
        items_data.append([f"{idx} {item.description}", f"{item.quantity}", f"N {item.unit_price:.2f}", f"N {item.total_price():.2f}"])

    # Totals Section
    items_data += [["", "", "Subtotal", f"N {invoice.total_before_tax():.2f}"],
                   ["", "", "Tax", f"N {invoice.tax_amount():.2f}"],
                   ["", "", "Total", f"N {invoice.total_amount():.2f}"],
                   ["", "", "Received", f"N {received_amount:.2f}"],  # Received amount from user input
                   ["", "", "Balance Due", f"N {balance_due:.2f}"]]   # Calculated balance due
    
    table_items = Table(items_data, colWidths=[1.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table_items.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(table_items)

    # Building the PDF with watermark support
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: WatermarkedCanvas(*args, logo_path=logo_path, **kwargs))
    print(f"Invoice saved as {filename}")
# JSON Data Handling
def load_data(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def save_invoice(invoice):
    invoices = load_data(INVOICES_FILE)
    invoices.append(invoice.to_dict())
    save_data(invoices, INVOICES_FILE)
    print("Invoice saved to invoices.json")

def save_customer(customer):
    customers = load_data(CUSTOMERS_FILE)
    customers.append(customer.to_dict())
    save_data(customers, CUSTOMERS_FILE)
    print("Customer saved to customers.json")

# CLI Interface
def display_menu():
    print("\nWelcome to the Invoice Generator!")
    print("1. Create a new invoice")
    print("2. View saved invoices")
    print("3. Add a new customer")
    print("4. Exit")

def create_invoice(logo_path=None):
    print("\nCreating a new invoice...")
    
    # Customer details input
    customer_name = input("Enter the customer's name: ")
    customer_address = input("Enter the customer's address: ")
    customer_email = input("Enter the customer's email: ")

    customer = Customer(customer_name, customer_address, customer_email)
    save_customer(customer)

    # Invoice items input
    items = []
    while True:
        description = input("Enter item description: ")
        quantity = int(input("Enter quantity: "))
        unit_price = float(input("Enter unit price: "))
        items.append(InvoiceItem(description, quantity, unit_price))

        another = input("Add another item? (y/n): ")
        if another.lower() != 'y':
            break

    invoice = Invoice(customer, items)

    # Input the received amount from the user
    total_amount = invoice.total_amount()
    print(f"The total amount for this invoice is: N {total_amount:.2f}")
    received_amount = float(input("Enter the received amount: "))
    
    # Calculate the balance due
    balance_due = total_amount - received_amount
    print(f"Balance due is: N {balance_due:.2f}")

    # Generate and save the invoice PDF
    filename = f"{invoice.invoice_number}.pdf"
    generate_invoice_pdf(invoice, filename, logo_path, received_amount, balance_due)

    save_invoice(invoice)
    print(f"Invoice generated and saved as {filename}\n")

def view_invoices():
    invoices = load_data(INVOICES_FILE)
    if not invoices:
        print("No invoices found.")
        return
    for invoice in invoices:
        print(f"Invoice #{invoice['invoice_number']}, Total: #{invoice['total_amount']}, Date: {invoice['date']}")

def add_customer():
    customer_name = input("Enter the customer's name: ")
    customer_address = input("Enter the customer's address: ")
    customer_email = input("Enter the customer's email: ")

    customer = Customer(customer_name, customer_address, customer_email)
    save_customer(customer)

def main():
    logo_path = "Fayina_Couture_Logo_2-removebg-preview.png"  # Make sure this is a valid path to the logo image
    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ")
        if choice == '1':
            create_invoice(logo_path)  # Pass the logo_path to ensure the logo is included
        elif choice == '2':
            view_invoices()
        elif choice == '3':
            add_customer()
        elif choice == '4':
            print("Exiting the Invoice Generator.")
            sys.exit()
        else:
            print("Invalid choice. Please select a valid option.")
# Example Usage
if __name__ == "__main__":
    main()
