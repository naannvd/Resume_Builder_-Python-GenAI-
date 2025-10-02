import pdfminer
from pdfminer.high_level import extract_text

def extract_pdf_text(file_path):
    return extract_text(file_path)
if(__name__ == "__main__"):
    file_path = "D:\Work\DevGate\CV Converter\\test resume.pdf"  # Replace with your PDF file path
    text = extract_pdf_text(file_path)
    print(text)