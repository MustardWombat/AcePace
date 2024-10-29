import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("key.env")

# Access the OpenAI API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Test if API key is loaded
if not openai.api_key:
    print("Error: OpenAI API key not found. Please check your key.env file.")
else:
    try:
        # Make a test API call to verify the key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, can you confirm my API key works?"}]
        )
        print("API Key is valid. Response received:", response['choices'][0]['message']['content'])

    except Exception as e:
        print("An error occurred:", e)
