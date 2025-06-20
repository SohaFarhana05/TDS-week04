from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/outline", response_class=PlainTextResponse)
async def get_outline(country: str = Query(..., description="Country name")):
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        return f"❌ Could not load Wikipedia page: {str(e)}"

    soup = BeautifulSoup(response.text, 'lxml')

    # Extract title from first <h1>
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else country

    # Extract headings
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    markdown = "## Contents\n\n"
    markdown += f"# {title}\n\n"

    for tag in headings:
        level = int(tag.name[1])
        text = tag.get_text(strip=True).replace("[edit]", "")
        if text and "Coordinates" not in text:
            markdown += f"{'#' * level} {text}\n\n"

    return markdown.strip()
