import os
import logging
from mcp.server.fastmcp import FastMCP
from crawl_service import perform_crawl
from search_service import perform_web_search

# Basic logging config
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

port = int(os.getenv("PORT", "8000"))
mcp = FastMCP("web-search-mcp", host="0.0.0.0", port=port)

@mcp.tool()
async def web_search(query: str) -> str:
    """
    Searches the web via SearXNG for current information. Returns top 3 results with titles and URLs.

    Args: 
        query: The search query
    """
    return await perform_web_search(query)

@mcp.tool()
async def crawl_url(url: str) -> str:
    """
    Crawls a website and returns cleaned, text-only markdown. Use this tool when you need to read 
    the content of a specific URL found in search results.

    Args: 
        url: The URL to crawl (must be http or https)
    """
    return await perform_crawl(url)

if __name__ == "__main__":
    mcp.run(transport="sse")
