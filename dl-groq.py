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
        "Drivers License Image. Respond ONLY with a valid JSON object matching this schema:\n"
        "{\n"

        "  'real_id_compliant': 'string or null'\n"
        "  'document_number': 'string or null'\n"
        "  'last_name': 'string or null'\n"
        "  'first_name': 'string or null'\n"
        "  'middle_name': 'string or null'\n"
        "  'suffix': 'string or null'\n"
        "  'date_of_birth': 'string or null'\n"
        "  'date_of_expiration': 'string or null'\n"
        "  'sex': 'string or null'\n"

        "  'height': 'string or null'\n"
        "  'eye_color': 'string or null'\n"
        "  'address_street': 'string or null'\n"
        "  'address_city': 'string or null'\n"
        "  'address_state': 'string or null'\n"
        "  'address_zip': 'string or null'\n"
        "  'restrictions': 'string or null'\n"
        "  'endorsements': 'string or null'\n"
        "  'organ_donor': 'string or null'\n"
        "  'medical_indicator': 'string or null'\n"


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
                            "text": "Carefully read the Drivers License image, including slurred or merged inline fields. Extract the required data points."
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
        max_tokens=900  # max token limit 1024
    )

    return chat_completion.choices[0].message.content


image_path = "DL.jpeg"
print('invoking ocr model.diplaying  Drivers Lincese data in schema begining')
print(birth_cert_ocr(image_path))
print('invoking ocr model..diplaying DL  data Ending')
