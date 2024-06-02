from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
import csv
from RPA.PDF import PDF
from pypdf import PdfReader, PdfWriter, Transformation
from PIL import Image
from RPA.Tables import Tables
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    open_robot_order_website()
    download_and_save_orders_csv()
    place_orders_from_csv()
    create_zip_and_add_all_receipt()
    

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
#    close_annoying_modal()

def close_annoying_modal():
    page = browser.page()
    page.click("button:Text('OK')")

def download_and_save_orders_csv():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def place_orders_from_csv():
    library = Tables()
    orders = library.read_table_from_csv(path="orders.csv", header=True)
    for row in orders:
        fill_the_form(row)
        store_receipt_as_pdf(row["Order number"])
        click_on_order_another_robot_button()
        archive_receipts()
    
def fill_the_form(row):
    close_annoying_modal()
    page = browser.page()
    success = False;
    while(success is False): 
        page.select_option("#head", row["Head"])
        page.click("#id-body-" + row['Body'])
        page.get_by_placeholder("Enter the part number for the legs").fill(row["Legs"])
        page.fill("#address", row["Address"])
        page.click("#order")
        success = page.query_selector("#receipt") is not None

def store_receipt_as_pdf(orderNumber):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdfFileName = "output/receipt" + orderNumber + ".pdf"
    pdf = PDF()
    pdf.html_to_pdf(receipt, pdfFileName)
    embed_screenshot_to_receipt(make_screenshot_of_robot(orderNumber), pdfFileName)

def click_on_order_another_robot_button():
    page = browser.page()
    page.click("#order-another")

def make_screenshot_of_robot(orderNumber):
    page = browser.page()
    previewImage = page.locator("#robot-preview-image")
    bytes = browser.screenshot(previewImage)
    fileName = "output/robot-" + orderNumber + ".png"
    write_file(fileName, bytes)
    return fileName;

def write_file(filename, bytes):
    with open(filename, "wb") as binary_file:
        binary_file.write(bytes)

def embed_screenshot_to_receipt(screenshot, pdf_file):

    base_pdf = PdfReader(pdf_file)
    image = Image.open(screenshot)
    image.save(screenshot + ".pdf")
    imagePdf = PdfReader(screenshot + ".pdf")
    imagePage = imagePdf.pages[0]
    
    base_page = base_pdf.pages[0]
    base_page.merge_page(imagePage)

    newPdf = PdfWriter()
    newPdf.add_page(base_page)
    newPdf.write(pdf_file)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip(folder="./output", archive_name="./output/receipts.zip", include="receipt*.pdf", exclude="/output/.*")
