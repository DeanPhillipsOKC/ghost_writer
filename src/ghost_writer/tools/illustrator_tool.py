from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import openai
import base64
import os

class IllustratorToolInput(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation.")

class IllustratorTool(BaseTool):
    name: str = "GPT-4o Image Generator"
    description: str = "Generates an image using GPT-4o (DALL·E 3) based on a text prompt."
    args_schema: Type[BaseModel] = IllustratorToolInput
    filename: str = "output.png"
    size: str = "1024x1024"

    def _run(self, prompt: str) -> str:
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Use the new client
            response = client.images.generate(
                model="gpt-image-1", 
                prompt=prompt,
                size=self.size,
                n=1,
            )
            image_data = response.data[0].b64_json
            with open(self.filename, 'wb') as f:
                f.write(base64.b64decode(image_data))
            return f"Image generated and saved to {self.filename}."
        except Exception as e:
            return f"Failed to generate image: {e}"
