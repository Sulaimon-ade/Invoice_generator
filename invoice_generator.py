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



from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import utils
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import utils
from reportlab.pdfgen.canvas import Canvas

# Function to draw the logo in the bottom-right corner
def draw_logo_footer(canvas, logo_path):
    canvas.saveState()
    if logo_path:
        try:
            logo = utils.ImageReader(logo_path)
            img_width, img_height = logo.getSize()
            aspect = img_height / float(img_width)
            canvas.drawImage(logo, 450, 30, width=100, height=100 * aspect)  # Place it in the bottom-right corner
        except Exception as e:
            print(f"Error loading footer logo: {e}")
    canvas.restoreState()

# Function to draw the watermark on every page (lower center of the page)
def draw_watermark(canvas, logo_path):
    canvas.saveState()
    if logo_path:
        try:
            canvas.setFillGray(0.9, 0.15)  # Further increase transparency
            logo = utils.ImageReader(logo_path)
            canvas.drawImage(logo, 200, 400, width=150, height=200, mask='auto')  # Lower center placement
        except Exception as e:
            print(f"Error loading watermark: {e}")
    canvas.restoreState()

# Custom Canvas to handle watermark and footer logo
class CustomCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        self.logo_path = kwargs.pop('logo_path', None)
        super().__init__(*args, **kwargs)

    def showPage(self):
        # Draw the watermark on every page
        if self.logo_path:
            draw_watermark(self, self.logo_path)
        super().showPage()

    def onFirstPage(self, *args, **kwargs):
        # Draw the logo in the footer on every page
        if self.logo_path:
            draw_logo_footer(self, self.logo_path)
        super().onFirstPage(*args, **kwargs)

# Function to generate the PDF invoice with logo and watermark
def generate_invoice_pdf(invoice, filename, logo_path=None, received_amount=0, balance_due=0):
    pdf = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    styles['Title'].alignment = TA_CENTER

    # Title and Date Section
    title = Paragraph(f"<b>INVOICE</b><br/>Invoice No: {invoice.invoice_number}", styles['Title'])
    date = Paragraph(f"Date: {invoice.date}", styles['Normal'])

    elements.append(title)
    elements.append(Spacer(1, 12))
    elements.append(date)
    elements.append(Spacer(1, 12))

    # Customer and Company Info
    customer_info = Paragraph(f"<b>Billed To:</b><br/>{invoice.customer.name}<br/>{invoice.customer.address}<br/>{invoice.customer.email}", styles['Normal'])
    company_info = Paragraph(f"<b>Fayina Luxuty Couture</b><br/>Block E2 Abu gidado street,wuye, Abuja, Nigeria Abuja<br/>Contact: fayinaluxurycouture@yahoo.com<br/>Phone: +2349032837162", styles['Normal'])

    table_info = [[customer_info, company_info]]
    table_header = Table(table_info, colWidths=[3 * inch, 3 * inch])
    elements.append(table_header)
    elements.append(Spacer(1, 12))

    # Line Items Section
    items_data = [["#", "Item", "Qty", "Unit Price", "Total"]]
    for idx, item in enumerate(invoice.items, start=1):
        items_data.append([f"{idx}", item.description, item.quantity, f"N {item.unit_price:.2f}", f"N {item.total_price():.2f}"])

    # Reduce the empty rows dynamically based on the number of items
    max_items = 3  # Reduce maximum item space to balance layout
    if len(invoice.items) < max_items:
        extra_space = max_items - len(invoice.items)
        for _ in range(extra_space):
            items_data.append(["", "", "", "", ""])

    # Totals Section
    items_data += [["", "", "", "Subtotal", f"N {invoice.total_before_tax():.2f}"],
                   ["", "", "", "Tax", f"N {invoice.tax_amount():.2f}"],
                   ["", "", "", "Total", f"N {invoice.total_amount():.2f}"],
                   ["", "", "", "Received", f"N {received_amount:.2f}"],
                   ["", "", "", "Balance Due", f"N {balance_due:.2f}"]]

    table_items = Table(items_data, colWidths=[0.5 * inch, 3.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table_items.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ]))
    elements.append(table_items)

    elements.append(Spacer(1, 12))

    # Footer Section
    footer = Paragraph("""
    <b>Thank you for your business!</b><br/>
    Payment can be made to:<br/>
    Your Company Name<br/>
    GTB Bank Plc, 0214413459<br/><br/>
    <b>Payment Policy:</b><br/>
    Payment is due within 14 days from the date of invoice. Late payments may incur a late fee of 1.5% per month on any outstanding balance. 
    Please ensure payments are made to the account provided above. If you have any questions or concerns regarding this invoice, kindly contact 
    us at fayinaluxurycouture@yahoo.com.<br/><br/>
    Thank you for your prompt payment and continued business.
    """, styles['Normal'])
    elements.append(footer)

    # Create the PDF with both watermark and logo handling
    pdf.build(elements, canvasmaker=lambda *args, **kwargs: CustomCanvas(*args, logo_path=logo_path, **kwargs))

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
    logo_path = "static/Fayina_Couture_Logo_2-removebg-preview.png"  # Make sure this is a valid path to the logo image
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
