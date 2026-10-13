from pathlib import Path
from pypdf import PdfReader
import pymupdf

pdf_form_data = {}


def extract_data_from_pdf(pdf_path):

    print(f" pdf path in method........... {pdf_path}")

    pdfreader = PdfReader(pdf_path)

    # pdfreader.get_fields()  # returns dictionary .
    form_fields = pdfreader.get_form_text_fields()

    print(f"form_fields {form_fields}")

    if not form_fields:
        print(" No Form Feilds fetched")
        return {}


def extract_data_from_pymupdf(pdf_path):
    document = pymupdf.open(pdf_path)

    for pageNo, pdfpage in enumerate(document):
        for widget in pdfpage.widgets():
            fieldName = widget.field_name
            fieldValue = widget.field_value
            print(f"fieldName : {fieldName}")
            print(f"fieldValue : {fieldValue}")

            pdf_form_data[fieldName] = fieldValue

        document.close()
        return pdf_form_data


print('---using pypdf')
extract_data_from_pdf('declaration.pdf')
print('----pypdf display end')

print('end printing data from using pypdf')
# Testing with pymupdf
print('Displaying form field data using pymupdf')
extract_data_from_pymupdf(
    'declaration.pdf')
print('Displayed form data finished using pymupdf.'
      )
