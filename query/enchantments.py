from google.genai import Client
from requests import get
from json import loads
import os
import re


PROMPT = """<source>
%s
</source>

Turn this into a JSON document for me. Do NOT wrap the response in markdown code blocks (no ```json). Output raw text only.

Format it exactly as:

{
    "{book name}": {
       "internal_id": "{internal id}",
       "levels": {
          "1": {
             "formatted_name": "{book name} I",
             "combinable": {boolean}
          }
       }
    }
}
"""


_ENCHANTMENT_INTERNAL_ID_OVERRIDES = {
    'Dragon Tracer': 'AIMING',
}


def _to_internal_id(book_name: str) -> str:
    if book_name in _ENCHANTMENT_INTERNAL_ID_OVERRIDES:
        return _ENCHANTMENT_INTERNAL_ID_OVERRIDES[book_name]

    return re.sub(r'[^A-Za-z0-9]+', '_', book_name).strip('_').upper()


def extract(client: Client) -> dict:
    print("Extracting enchantments...")
    page = get('https://hypixelskyblock.minecraft.wiki/w/Enchantments').text
    print("Extracting ultimate enchantments...")
    ultimate_page = get('https://hypixelskyblock.minecraft.wiki/w/Ultimate_Enchantments').text

    print("Parsing enchantments...")
    model = os.getenv('GENAI_MODEL')
    if not model:
        raise RuntimeError('GENAI_MODEL is not set')

    # Parse regular enchantments
    response = client.models.generate_content(
        model=model,
        contents=PROMPT % page,
    )
    response_text = response.text
    if not response_text:
        raise ValueError('Empty response from model')

    print(response_text)
    data = loads(response_text)

    # Parse ultimate enchantments
    response_ultimate = client.models.generate_content(
        model=model,
        contents=PROMPT % ultimate_page,
    )
    response_ultimate_text = response_ultimate.text
    if response_ultimate_text:
        print(response_ultimate_text)
        ultimate_data = loads(response_ultimate_text)
        # Merge ultimate enchantments into main data and mark all levels as combinable
        for book_name, enchantment in ultimate_data.items():
            if isinstance(enchantment, dict) and 'levels' in enchantment:
                for level_data in enchantment['levels'].values():
                    if isinstance(level_data, dict):
                        level_data['combinable'] = True
        data.update(ultimate_data)

    for book_name, enchantment in data.items():
        if isinstance(enchantment, dict):
            enchantment['internal_id'] = _to_internal_id(book_name)

    return data
