import cv2
import pytesseract
import re
import pandas as pd
import json

# method for extract text from image

# install Tesseract-OCR for opering system you are working on
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
formData = {}


def textFromImage(imagePath):
    # OpenCV Preprocessing Image--gray scale conversion for OCR .
    img = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
    grayImageRaw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # for sig/dates on line
    threshold = cv2.threshold(
        grayImageRaw, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # detect horizontal lines
    horizontal_line = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(
        threshold, cv2.MORPH_OPEN, horizontal_line, iterations=2)
    # remove the detected lines by painting over them in inverted image
    cnts = cv2.findContours(
        detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # dealing with binary image countours.
    # defining countours to get data signed or date on line instead of text fields.
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for cnt in cnts:
        cv2.drawContours(threshold, [cnt], -1, (0, 0, 0), 2)
    # revert back to normal black text

    grayImage = cv2.bitwise_not(threshold)

    customConfig = r'--oem 1 --psm 6'

    grayImageText = pytesseract.image_to_string(grayImage, config=customConfig)

    print(f'grayImageText : {grayImageText}')

    return grayImageText


def parseGrayImageData(grayImageText):

    required_fields = [
        "Name of applicant",
        "Day phone number",
        "Address",
        "City",
        "State",
        "Zip code",
        "Email address",
        "Full name",
        "Date of birth",
        "Sex",
        "City of birth",
        "County of birth"
    ]
    # populate fields
    formData = {field: "" for field in required_fields}
    lines = grayImageText.splitlines()
    stripedLines = [line.strip() for line in lines if line.strip()]

    for fieldName in required_fields:

        for idx, line in enumerate(stripedLines):
            if fieldName.lower() in line.lower():
                valueInSameLine = re.search(
                    r"[:\-\]\)]\s*(.*)$", line
                ) or re.search(rf"{re.escape(fieldName)}\s+(.+)$", line, re.IGNORECASE)
                if valueInSameLine and valueInSameLine.group(1).strip():
                    fieldValue = valueInSameLine.group(1).strip()
                if not any(fieldTemp.lower() in fieldValue.lower() for fieldTemp in required_fields):
                    formData[fieldName] = fieldValue
                    break
        # check for empty line check next 3 lines

            for checkForward in range(1, 4):
                if idx + checkForward < len(stripedLines):
                    nextLine = stripedLines[idx+checkForward]

                if any(
                    f.lower() in nextLine.lower()
                    for f in required_fields
                ):
                    break

                if nextLine:
                    formData[fieldName] = nextLine
                break
        break

        return formData

# -----------parsers


def parseGrayImageDataNew(grayImageText):
    # Mapping table of canonical key properties to variations or patterns seen in the text
    field_rules = {
        "Name of applicant": r"Name of applicant:\s*“?(.*?)(?=Day phone|$)",
        "Day phone number": r"Day phone number,\s*([\d\s~\-\.O]+)",
        "Address": r"Addsess.*?-\s*\n?(.*)",
        "Email address": r"Email Address\.\s*(.*)",
        "Full name": r"Full Name,\s*(.*)",
        "Date of birth": r"Date of birth,\s*([^\s_]+)",
        "Sex": r"Sex_([^_]+)_",
        "City of birth": r"City of birth,\s*([^\s\n,]+)",
        "County of birth": r"County of birth:\s*(.*)"
    }

    # Simple direct fallbacks using fuzzy inclusion if regex blocks are too strict
    fuzzy_keywords = {
        "City": "City:",
        "State": "Sate,",
        "Zip code": "Zp code"
    }

    formData = {field: "" for field in field_rules}
    for k in fuzzy_keywords:
        formData[k] = ""

    lines = grayImageText.splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]

    # 1. Process fields governed by Regex Rules (Handles inline multi-fields)
    for field, pattern in field_rules.items():
        match = re.search(pattern, grayImageText, re.IGNORECASE)
        if match:
            val = match.group(1).strip(" “\"_-,.")
            # Clean up known digital conversions like O -> 0
            if field == "Day phone number":
                val = val.replace("O", "0").replace("~", "-")
            formData[field] = val

    # 2. Process simpler location layouts that fall on structural break lines
    for field, keyword in fuzzy_keywords.items():
        for idx, line in enumerate(clean_lines):
            if keyword.lower() in line.lower():
                # Attempt to extract text right after the label indicator
                parts = re.split(r"[:,\-\s]\s*", line, maxsplit=1)
                if len(parts) > 1 and parts[1].strip():
                    formData[field] = parts[1].strip()
                else:
                    # Lookahead safely to the next line if empty
                    if idx + 1 < len(clean_lines):
                        formData[field] = clean_lines[idx + 1]
                break

    return formData


# --------- end of custom parsing

imgFile = 'birth_certificate_hand_written.jpeg'

rawImgData = textFromImage(imgFile)

# parsedImageData = parseGrayImageData(rawImgData)

parsedImageDataNew = parseGrayImageData(rawImgData)


print(json.dumps(parsedImageDataNew, indent=4))
