from groq import Groq
import base64
import os
from dotenv import load_dotenv
from pathlib import Path


# ==========================================
# 1. PATH RESOLUTION & SETUP
# ==========================================
# script_dir = Path(__file__).resolve().parent
# project_root = script_dir.parent
load_dotenv(".env")
# os.environ.get("GROQ_API_KEY")  when env variable set ...os.getenv () when retreiving from .env file


# Function to encode the image


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def birth_cert_ocr(image_path):
    # Encode image
    base64_image = encode_image(image_path)

    # Define image schema from your image in System Prompt to model
    system_prompt = (
        "You are an expert document processing OCR Agent. Extract information from this "
        "handwritten birth certifate form. Respond ONLY with a valid JSON object matching this schema:\n"
        "{\n"

        "  'Name of applicant': 'string or null'\n"
        "  'Day phone number': 'string or null'\n"
        "  'Address': 'string or null'\n"
        "  'Email address': 'string or null'\n"
        "  'Full name': 'string or null'\n"
        "  'Date of birth': 'string or null'\n"
        "  'Sex': 'string or null'\n"
        "  'City of birth': 'string or null'\n"
        "  'County of birth': 'string or null'\n"


        "}"
    )

    # Getting the base64 string
    base64_encoded_image = encode_image(image_path)
    # GROQ_API_KEY
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
        # Ensure this vision model is active on your tier
        model="qwen/qwen3.8-27b",
        # Forces the model to return valid JSON
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                        {
                            "type": "text",
                            "text": "Carefully read the handwriting in this image, including slurred or merged inline fields. Extract the required data points."
                        },
                    {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                    },
                ],
            }
        ],
        temperature=0.1,  # Low temperature for precise, deterministic extraction
        max_tokens=1024
    )

    return chat_completion.choices[0].message.content


image_path = "birth_certificate_hand_written.jpeg"
print('invoking ocr model..diplaying data in schema begining')
print(birth_cert_ocr(image_path))
print('invoking ocr model..diplaying data Ending')
