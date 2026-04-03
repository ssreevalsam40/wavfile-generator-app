import httpx
from bs4 import BeautifulSoup
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
from typing import Optional


class TextGenerator:
    """Handles website crawling and script generation using Vertex AI."""

    def __init__(self, project_id: str, location: str = "us-central1", credentials: Optional[any] = None):
        """Initializes Vertex AI with the given project, location and credentials."""
        self.project_id = project_id
        self.location = location
        vertexai.init(project=self.project_id, location=self.location, credentials=credentials)
        self.model = GenerativeModel("gemini-2.5-flash")

    def crawl_website(self, url: str) -> str:
        """Crawls the given URL and extracts the text content."""
        try:
            response = httpx.get(url, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text from relevant tags
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text = soup.get_text(separator=' ', strip=True)
            return text[:5000]  # Limit to 5000 characters for token efficiency
        except Exception as e:
            return f"Error crawling website: {str(e)}"

    def generate_script(self, url: str, scenario: str) -> str:
        """Generates a dialogue script between an AU agent and customer."""
        website_content = self.crawl_website(url)
        
        prompt = f"""
        You are a highly professional scriptwriter specializing in Australian customer service scenarios.
        
        CONTEXT:
        The following text is from the company's website (use this for brand tone and context):
        ---
        {website_content}
        ---
        
        SCENARIO:
        {scenario}
        
        REQUIREMENTS:
        - Write a dialogue script between two people:
            1. [Agent]: A female Australian agent (professional, friendly, helpful).
            2. [Customer]: A male Australian customer (direct, slightly informal but polite).
        - Use Australian English spelling (e.g., 'organisation', 'authorised', 'programme', 'labour').
        - Use local Australian terminology where appropriate (e.g., 'G'day', 'Cheers', 'No worries' for the customer).
        - Ensure the tone matches the branding found on the website. Never mention the company or brand name anywhere in the audio file
        - Format the output as:
          [Agent]: Text...
          [Customer]: Text...
        
        Keep it concise (around 4-6 turns each).
        """
        
        response = self.model.generate_content(prompt)
        return response.text


def example_text_generation(project_id: str, url: str, scenario: str, credentials: Optional[any] = None):
    """Example function to demonstrate TextGenerator functionality."""
    generator = TextGenerator(project_id=project_id, credentials=credentials)
    script = generator.generate_script(url, scenario)
    print("Generated Script:\n")
    print(script)
    return script
