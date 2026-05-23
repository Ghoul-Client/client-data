from google.genai import Client
from requests import get
from json import loads
import os


PROMPT = """<source>
%s
</source>

Turn this into a JSON document for me. Do NOT wrap the response in markdown code blocks (no ```json). Output raw text only.

Format it exactly as:

{
    "{book name}": {
       "levels": {
          "1": {
             "formatted_name": "{book name} I",
             "combinable": {boolean}
          }
       }
    }
}
"""


def extract(client: Client) -> dict:
    print("Extracting enchantments...")
    page = get('https://hypixelskyblock.minecraft.wiki/w/Enchantments').text
    print(page)
    print("Parsing enchantments...")
    response = client.models.generate_content(
        model=os.getenv('GENAI_MODEL'),
        contents={'text': PROMPT % page},
    )
    print(response.text)
    return loads(response.text)
