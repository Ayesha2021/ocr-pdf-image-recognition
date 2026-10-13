import pymupdf  # 🔄 Updated from 'import fitz'
import arabic_reshaper
from bidi.algorithm import get_display


def fix_arabic_text(text):
    if not text:
        return ""

    # Clean up messy newline formatting errors injected by PDF reader
    cleaned_text = text.replace('\n', ' ').strip()

    # Check if the cell contains Arabic characters
    if any('\u0600' <= char <= '\u06FF' for char in cleaned_text):
        # Shape the letters and apply correct right-to-left layout direction
        reshaped = arabic_reshaper.reshape(cleaned_text)
        # return get_display(reshaped)
        return reshaped

    return cleaned_text


# --- Run the Modernized Extractor Pipeline ---
# Use 'pymupdf' namespace explicitly instead of deprecated 'fitz'
doc = pymupdf.open("Para-1-First-Half-Rootwords.pdf")
page = doc[0]

tables = page.find_tables()
if tables:
    for table in tables:
        raw_rows = table.extract()

        # Apply the layout and Bidi text fix to every cell
        for row in raw_rows:
            fixed_row = [fix_arabic_text(cell) for cell in row]
            print(fixed_row)
