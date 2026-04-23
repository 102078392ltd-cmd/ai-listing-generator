"""
Core listing generation engine.

Connects to Azure OpenAI and generates:
- MLS listing descriptions
- Social media posts (Instagram, Facebook)
- Email marketing copy
- Full marketing packages (all of the above)
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from .prompts import (
    SYSTEM_PROMPT,
    get_system_prompt,
    build_user_prompt,
    SOCIAL_INSTAGRAM_PROMPT,
    SOCIAL_FACEBOOK_PROMPT,
    EMAIL_BLAST_PROMPT,
    FULL_PACKAGE_PROMPT,
)

load_dotenv()


class ListingEngine:

    def __init__(self, endpoint=None, api_key=None, api_version=None, deployment=None):
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version or os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
        )
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

    # ── Core generation method ───────────────────────────────
    def _generate(self, property_details, system_prompt, temperature=0.7):
        """Internal: send a prompt pair to Azure OpenAI and return the response."""
        user_prompt = build_user_prompt(property_details)

        response = self.client.chat.completions.create(
            model=self.deployment,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0].message.content.strip()

    # ── MLS Listing Description ──────────────────────────────
    def generate(self, property_details, temperature=0.7, system_prompt=None):
        """Generate an MLS listing description."""
        if system_prompt is None:
            prop_type = property_details.get("property_type", "")
            system_prompt = get_system_prompt(prop_type)

        return self._generate(property_details, system_prompt, temperature)

    def generate_variations(self, property_details, count=3, temperature=0.85):
        """Generate multiple MLS listing variations."""
        return [
            self.generate(property_details, temperature=temperature)
            for _ in range(count)
        ]

    # ── Social Media Posts ───────────────────────────────────
    def generate_social(self, property_details, platform="instagram", temperature=0.8):
        """Generate a social media post. Platform: 'instagram' or 'facebook'."""
        prompts = {
            "instagram": SOCIAL_INSTAGRAM_PROMPT,
            "facebook": SOCIAL_FACEBOOK_PROMPT,
        }
        system_prompt = prompts.get(platform.lower(), SOCIAL_INSTAGRAM_PROMPT)
        return self._generate(property_details, system_prompt, temperature)

    # ── Email Marketing ──────────────────────────────────────
    def generate_email(self, property_details, temperature=0.7):
        """Generate a new-listing email blast."""
        return self._generate(property_details, EMAIL_BLAST_PROMPT, temperature)

    # ── Full Marketing Package ───────────────────────────────
    def generate_full_package(self, property_details, temperature=0.75):
        """
        Generate a complete marketing package in one API call.
        Returns a dict with keys: 'mls', 'instagram', 'facebook', 'email'
        """
        raw = self._generate(property_details, FULL_PACKAGE_PROMPT, temperature)
        return self._parse_package(raw)

    @staticmethod
    def _parse_package(raw):
        """Parse the full-package response into sections."""
        sections = {"mls": "", "instagram": "", "facebook": "", "email": ""}

        header_map = {
            "MLS LISTING": "mls",
            "MLS": "mls",
            "INSTAGRAM": "instagram",
            "FACEBOOK": "facebook",
            "EMAIL": "email",
        }

        current_key = None
        current_lines = []

        for line in raw.splitlines():
            stripped = line.strip().strip("-").strip()

            if stripped in header_map:
                if current_key:
                    sections[current_key] = "\n".join(current_lines).strip()
                current_key = header_map[stripped]
                current_lines = []
            else:
                current_lines.append(line)

        if current_key:
            sections[current_key] = "\n".join(current_lines).strip()

        if not any(sections.values()):
            sections["mls"] = raw

        return sections
