from datetime import time
from typing import AnyStr, Type, Optional
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
from gentopia.tools.basetool import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
import time as sleep_time


class URLScannerArgs(BaseModel):
    query: str = Field(..., description="a search query")


class URLScanner(BaseTool):
    """Tool that adds the capability to query the Google search API."""

    name = "url_scanner"
    description = "Checks whether links are safe to visit"

    args_schema: Optional[Type[BaseModel]] = URLScannerArgs

    def _run(self, query: AnyStr) -> str:
        parsed_url = urlparse(query if query.startswith('http') else f"http://{query}")
        hostname = parsed_url.hostname or query
        if hostname.startswith("www."):
            hostname = hostname[4:]
        
        chrome_service = Service('/Users/abhi/nlp/Gentopia-Mason/Gentopia/gentopia/resource/chromedriver-mac-arm64/chromedriver') # Please change this with the path of your selenium webdriver compatible with your chrome version.
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.get(f'https://www.urlvoid.com/scan/{hostname}/')
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        if soup.find("h1", text="Report Not Found"):
            print("Report not found, submitting the query manually.")
            try:
                input_element = driver.find_element("css selector", "body > div:nth-child(2) > div > div > div > form > div > input")
                input_element.send_keys(hostname)
                
                submit_button = driver.find_element("css selector", "body > div:nth-child(2) > div > div > div > form > div > span > button")
                submit_button.click()
                
                sleep_time.sleep(3)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
            except Exception as e:
                print(f"Error while trying to submit the form: {e}")
        
        table_rows = soup.find_all("tr")
        detection_status = None
        detection_score = None

        driver.quit()

        for row in table_rows:
            if "Detections Counts" in row.get_text():
                detection_span = row.find("span", class_=["label-danger", "label-success"])
                if detection_span:
                    detection_score = detection_span.text.strip()
                    
                    if "label-danger" in detection_span["class"]:
                        detection_status = "UNSAFE"
                    elif "label-success" in detection_span["class"]:
                        detection_status = "SAFE"
                break

        if detection_status and detection_score:
            return f"{hostname} is: [{detection_status}] to visit."
        else:
            return f"Unable to scan {hostname}"
            
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = URLScanner()._run("Attention for transformer")
    print(ans)
