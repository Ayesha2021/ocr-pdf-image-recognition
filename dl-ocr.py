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
        "document_type": "",
        "real_id_compliant": "",
        "document_number": "",
        "last_name": "",
        "first_name": "",
        "middle_name": "",
        "suffix": "",
        "date_of_birth": "",
        "date_of_expiration": "",
        "sex": "",
        "height": "",
        "eye_color": "",
        "address_street": "",
        "address_city": "",
        "address_state": "",
        "address_zip": "",
        "restrictions": "",
        "endorsements": "",
        "organ_donor": "",
        "medical_indicator": ""
    }

    formData = {field: "" for field in field_rules}

    lines = grayImageText.splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]

    # 1. Process fields governed by Regex Rules (Handles inline multi-fields)
    for field, pattern in field_rules.items():
        match = re.search(pattern, grayImageText, re.IGNORECASE)
        if match:
            # Clean up known digital conversions like O -> 0
            val = match.group(1)
            formData[field] = val

    # 2. Process simpler location layouts that fall on structural break lines

    return formData


# --------- end of custom parsing

imgFile = 'DL.jpeg'

rawImgData = textFromImage(imgFile)

# parsedImageData = parseGrayImageData(rawImgData)

parsedImageDataNew = parseGrayImageData(rawImgData)


print(json.dumps(parsedImageDataNew, indent=4))
