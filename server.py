import uvicorn
import os
import logging
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route

# Basic logging config
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# Import business logic
from crawl_service import perform_crawl
from search_service import perform_web_search

# --- MCP Server Setup ---

mcp = Server("web-search-mcp")

@mcp.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="web_search",
            description="Searches the web via SearXNG for current information. Returns top 3 results with titles and URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="crawl_url",
            description="Crawls a website and returns cleaned, text-only markdown. Use this tool when you need to read the content of a specific URL found in search results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to crawl (must be http or https)"
                    }
                },
                "required": ["url"]
            }
        )
    ]

@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "web_search":
        query = arguments.get("query")
        if not query:
            raise ValueError("Query is required")
        
        content = await perform_web_search(query)
        return [TextContent(type="text", text=content)]

    elif name == "crawl_url":
        url = arguments.get("url")
        if not url:
            raise ValueError("URL is required")
        
        content = await perform_crawl(url)
        return [TextContent(type="text", text=content)]
    
    raise ValueError(f"Unknown tool: {name}")

# --- Starlette / SSE Setup ---

sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())

async def handle_messages(request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
