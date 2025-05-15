from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from markdown_pdf import MarkdownPdf, Section
import os

# Define the input schema
class MarkdownToPDFInput(BaseModel):
    markdown_path: str = Field(..., description="Path to the input Markdown file.")
    output_pdf_path: str = Field(..., description="Path where the output PDF will be saved.")

# Define the custom tool
class MarkdownToPDFTool(BaseTool):
    name: str = "Markdown to PDF Converter"
    description: str = "Converts a Markdown file into a PDF document."
    args_schema: Type[BaseModel] = MarkdownToPDFInput

    def _run(self, markdown_path: str, output_pdf_path: str) -> str:
        # Check if the markdown file exists
        if not os.path.exists(markdown_path):
            return f"Markdown file not found: {markdown_path}"

        # Read the markdown content
        with open(markdown_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Create a PDF with a table of contents up to level 2
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(md_content))
        pdf.meta["title"] = os.path.basename(markdown_path)
        pdf.save(output_pdf_path)

        return f"PDF successfully created at: {output_pdf_path}"
