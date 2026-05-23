from dotenv import load_dotenv
from google import genai
from json import dumps
import query.enchantments
import os

load_dotenv()

def quick_write(content: dict, filename: str):
    with open('data/' + filename, 'w') as f:
        f.write(dumps(content, indent=4))

if __name__ == "__main__":
    client = genai.Client(api_key=os.getenv('GENAI_API_KEY'))

    print("Writing enchantments.json...")
    quick_write(query.enchantments.extract(client), 'enchantments.json')
