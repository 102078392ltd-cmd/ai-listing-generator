"""
Core listing generation engine.
Connects to Azure OpenAI and generates MLS-ready property descriptions.
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from .prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()


class ListingEngine:
    """
    Generates real estate listing descriptions using Azure OpenAI.

    Usage:
        engine = ListingEngine()
        description = engine.generate({
            "property_type": "Bungalow",
            "bedrooms": 3,
            "bathrooms": 2,
            "sqft": 1150,
            "neighbourhood": "Cathedral",
            "features": ["hardwood floors", "updated kitchen", "fenced yard"]
        })
        print(description)
    """

    def __init__(self, endpoint=None, api_key=None, api_version=None, deployment=None):
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Missing Azure OpenAI credentials. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in your .env file."
            )

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def generate(self, property_details, temperature=0.7, system_prompt=None):
        """Generate a listing description from property details."""
        user_prompt = build_user_prompt(property_details)

        response = self.client.chat.completions.create(
            model=self.deployment,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0].message.content.strip()

    def generate_variations(self, property_details, count=3, temperature=0.85):
        """Generate multiple variations for agents to choose from."""
        variations = []
        for _ in range(count):
            desc = self.generate(property_details, temperature=temperature)
            variations.append(desc)
        return variations
