"""
Core listing generation engine.

Connects to Azure OpenAI and generates:
- MLS listing descriptions
- Social media posts (Instagram, Facebook)
- Email marketing copy
- Full marketing packages (all of the above)
- Photo-based captions using GPT-4o Vision
"""

import os
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI
from .prompts import (
    SYSTEM_PROMPT,
    get_system_prompt,
    build_user_prompt,
    build_photo_context,
    SOCIAL_INSTAGRAM_PROMPT,
    SOCIAL_FACEBOOK_PROMPT,
    EMAIL_BLAST_PROMPT,
    FULL_PACKAGE_PROMPT,
    PHOTO_CAPTION_INSTAGRAM_PROMPT,
    PHOTO_CAPTION_FACEBOOK_PROMPT,
    PHOTO_DESCRIBE_PROMPT,
    PHOTO_CAROUSEL_INSTAGRAM_PROMPT,
    PHOTO_CAROUSEL_FACEBOOK_PROMPT,
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

    # ── Core text generation ─────────────────────────────────
    def _generate(self, property_details, system_prompt, temperature=0.7):
        """Internal: send a text prompt to Azure OpenAI and return the response."""
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

    # ── Core vision generation ───────────────────────────────
    def _generate_with_image(self, image_bytes, system_prompt, user_text="", temperature=0.7):
        """Send an image + optional text to GPT-4o Vision."""
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        user_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64_image}",
                    "detail": "high",
                },
            },
        ]

        if user_text:
            user_content.insert(0, {"type": "text", "text": user_text})

        response = self.client.chat.completions.create(
            model=self.deployment,
            temperature=temperature,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
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

    # ── Photo-Based Captions (GPT-4o Vision) ─────────────────
    def generate_photo_caption(self, image_bytes, property_details=None, platform="instagram", temperature=0.8):
        """Generate a social caption based on a listing photo using GPT-4o Vision."""
        prompts = {
            "instagram": PHOTO_CAPTION_INSTAGRAM_PROMPT,
            "facebook": PHOTO_CAPTION_FACEBOOK_PROMPT,
        }
        system_prompt = prompts.get(platform.lower(), PHOTO_CAPTION_INSTAGRAM_PROMPT)
        context = build_photo_context(property_details) if property_details else ""
        return self._generate_with_image(image_bytes, system_prompt, context, temperature)

    def describe_photo(self, image_bytes, temperature=0.5):
        """Generate a professional description of a listing photo."""
        return self._generate_with_image(image_bytes, PHOTO_DESCRIBE_PROMPT, "", temperature)
    
    def generate_carousel_caption(self, image_list, property_details=None, platform="instagram", temperature=0.8):
        """Generate one unified carousel caption from multiple listing photos using GPT-4o Vision."""
        prompts = {
            "instagram": PHOTO_CAROUSEL_INSTAGRAM_PROMPT,
            "facebook": PHOTO_CAROUSEL_FACEBOOK_PROMPT,
        }
        system_prompt = prompts.get(platform.lower(), PHOTO_CAROUSEL_INSTAGRAM_PROMPT)
        context = build_photo_context(property_details) if property_details else ""

        # Build content array with all images
        user_content = []
        if context:
            user_content.append({"type": "text", "text": context})

        for image_bytes in image_list:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64_image}",
                    "detail": "low",
                },
            })

        response = self.client.chat.completions.create(
            model=self.deployment,
            temperature=temperature,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )

        return response.choices[0].message.content.strip()

