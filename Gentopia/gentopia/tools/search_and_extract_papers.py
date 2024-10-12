import json
from typing import AnyStr, Optional, Type, Dict
from pydantic import BaseModel, Field
from io import BytesIO
from requests import get
from pypdf import PdfReader
from googlesearch import search
from gentopia.tools.basetool import *

class SearchAndExtractPapersArgs(BaseModel):
    query: str = Field(..., description="A search query for finding research papers in PDF format.")

class SearchAndExtractPapers(BaseTool):
    """Tool for searching PDFs on Google and extracting their text content."""

    name = "search_and_extract_papers"
    description = ("A tool that searches for research papers in PDF format using Google "
                   "and extracts the text content directly from the files without saving them locally.")

    args_schema: Optional[Type[BaseModel]] = SearchAndExtractPapersArgs

    def _run(self, query: AnyStr) -> Dict[str, AnyStr]:
        combined_payload = {"papers": []}
        print(f"Searching for: {query}")

        # Search Google for PDFs related to the query
        for result in search(f"{query} filetype:pdf"):
            print(f"Found URL: {result}")
            try:
                response = get(result, stream=True)
                # Check if the response contains PDF content
                if response.headers['Content-Type'] == 'application/pdf':
                    pdf_stream = BytesIO(response.content)
                    pdf_reader = PdfReader(pdf_stream)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""

                    return text
                 
                else:
                    print(f"Not a PDF: {result}")
                    return "no research papers found"
            except Exception as e:
                print(f"Error accessing {result}: {e}")
                return "no research papers found"

        # return combined_payload

    async def _arun(self, *args: AnyStr, **kwargs: AnyStr) -> str:
        raise NotImplementedError

if __name__ == "__main__":
    ans = SearchAndExtractPapers()._run("Attention for transformer")
    print(ans)
    
    # # Print the result as a formatted JSON string
    # print(json.dumps(result, indent=4))
