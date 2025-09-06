import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Load .env file
load_dotenv()

class PerplexityVisionClient:
    def __init__(self, api_key=None):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("Perplexity API key not provided.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )

    def process(self, image_path, context=""):
        try:
            prompt = f"""
            I have extracted text from a handwritten note using OCR, but it may contain errors.
            Please read and correct the following text, fixing any OCR mistakes and improving readability:
            
            OCR Text: {context}
            
            Please provide only the corrected, clean text without explanations.
            """

            response = self.client.chat.completions.create(
                model="sonar-medium-online",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at reading and correcting handwritten text from OCR output."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )

            corrected_text = response.choices[0].message.content.strip()
            return {
                'corrected_text': corrected_text, 
                'response_raw': response
            }

        except Exception as e:
            self.logger.error(f"Perplexity API call failed: {e}")
            return {
                'corrected_text': context, 
                'response_raw': None, 
                'error': str(e)
            }
