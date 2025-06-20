from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/outline")
def get_outline(country: str = Query(...)):
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    
    soup = BeautifulSoup(response.content, "lxml")
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    
    # Start with a single "## Contents" and country name
    markdown = f"## Contents\n\n# {country}\n\n"

    for heading in headings:
        text = heading.get_text(strip=True)

        # Skip duplicate or noisy headings
        if text.lower() in [country.lower(), "contents"]:
            continue

        level = int(heading.name[1])
        markdown += f"{'#' * level} {text}\n\n"

    return {"outline": markdown.strip()}

