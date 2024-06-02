from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
import csv
from RPA.PDF import PDF
from pypdf import PdfReader, PdfWriter, Transformation
from PIL import Image

@task
def place_robot_orders():
    go_to_website_and_accept_cookies()
    download_and_save_orders_csv()
    place_orders_from_csv()

def go_to_website_and_accept_cookies():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    accept_cookies()

def accept_cookies():
    page = browser.page()
    page.click("button:Text('OK')")

def download_and_save_orders_csv():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def place_orders_from_csv():
    with open("orders.csv") as ordersCsv:
        reader = csv.DictReader(ordersCsv)
        for row in reader:
            place_order(row)
            make_pdf_of_receipt(row)
            click_on_order_another_robot_button()
            accept_cookies()
    

def place_order(row):
    page = browser.page()
    success = False;
    while(success is False): 
        page.select_option("#head", row["Head"])
        page.click("#id-body-" + row['Body'])
        page.get_by_placeholder("Enter the part number for the legs").fill(row["Legs"])
        page.fill("#address", row["Address"])
        page.click("#order")
        success = page.query_selector("#receipt") is not None

def make_pdf_of_receipt(row):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdfFileName = "output/receipt" + row["Order number"] + ".pdf"
    pdf = PDF()
    pdf.html_to_pdf(receipt, pdfFileName)
    add_robot_to_pdf(pdfFileName, make_screenshot_of_robot(row))

def click_on_order_another_robot_button():
    page = browser.page()
    page.click("#order-another")

def make_screenshot_of_robot(row):
    page = browser.page()
    filename = "output/robot-" + row["Order number"] + ".png"
    bytes = browser.screenshot(page.locator("#robot-preview-image"))
    write_png_file(filename, bytes)
    return filename

def add_robot_to_pdf(pdfFileName, imageFileName):
    base_pdf = PdfReader(pdfFileName)
    image = Image.open(imageFileName)
    #image.resize(size=(190, 260))
    image.save(imageFileName + ".pdf")
    imagePdf = PdfReader(imageFileName + ".pdf")
    imagePage = imagePdf.pages[0]
    
    base_page = base_pdf.pages[0]
    base_page.merge_scaled_page(imagePage, 0.5)

    newPdf = PdfWriter()
    newPdf.add_page(base_page)
    newPdf.write(pdfFileName)


def write_png_file(name, bytes):
    with open(name, "wb") as binary_file:
        binary_file.write(bytes)