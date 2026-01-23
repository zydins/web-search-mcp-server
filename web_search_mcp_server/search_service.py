import httpx
import os
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8080")

async def perform_web_search(query: str) -> str:
    logger.info(f"Searching SearXNG for '{query}'")
    
    url = f"{SEARXNG_URL}/search"
    params = {
        "format": "json",
        "q": query
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("results", [])
            if not items:
                logger.info(f"No results for '{query}'")
                return json.dumps({"results": []})

            # Format as JSON
            results = []
            for item in items[:3]:
                title = item.get("title", "No Title")
                url = item.get("url", "")
                results.append({
                    "title": title,
                    "url": url
                })
                logger.info(f"Found result for '{query}': {title}, {url}")
            
            return json.dumps({"results": results}, indent=2)

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return json.dumps({"error": str(e)})
