import cv2
import pytesseract
import re
import pandas as pd

# method for extract text from image

# install Tesseract-OCR for opering system you are working on
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
fromData = {}


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

    grayImageText = pytesseract.image_to_string(grayImage)

    print(f'grayImageText : {grayImageText}')

    return grayImageText


def parseGrayImageData(grayImageText):

    required_fields = [

        "Candidate Full Legal Name",
        "Candidate Signature",
        "Date Completed"
    ]
    formData = {

    }
    lines = grayImageText.split('\n')
    print('Printing lenght of lines::::')
    print(len(lines))
    print('end printing len of lines')
    # search for pattern like Label: Value
    fieldName_toFindValue = None
    for line in lines:
        lineStr = line.strip()
        # print(lineStr)
        if not lineStr:
            continue

        if fieldName_toFindValue:
            formData[fieldName_toFindValue] = lineStr
            fieldName_toFindValue = None
            continue
        patternMatch = re.match(r"^\s*(.*?)\s*[:\-\]\)]\s*(.*)$", lineStr)

        if patternMatch:
            fieldName = patternMatch.group(1).strip()
            fieldValue = patternMatch.group(2).strip()
            if fieldName in required_fields:
                if fieldValue:
                    formData[fieldName] = fieldValue
                else:
                    fieldName_toFindValue = fieldName

    return formData


imgFile = 'declaration.png'

rawImgData = textFromImage(imgFile)

parsedImageData = parseGrayImageData(rawImgData)


print(parsedImageData)
