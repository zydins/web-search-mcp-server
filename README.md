# Web Search & Crawl MCP Server + SearXNG

A Docker-ready MCP server with **SearXNG** (privacy-focused search aggregator) + `crawl4ai` for full web access capabilities.

## How It Works

### 1. Web Search (`web_search`)
**Tool name: `web_search`**.

- **Privacy-focused**: Aggregates results from multiple engines without tracking.
- **Filtering**: Fetches the top 3 most relevant results.
- **Output**: JSON with `title` and `url` only.

### 2. Smart Web Crawler (`crawl_url`)
- **Headless Browsing**: `crawl4ai` (Playwright) for JS-heavy sites.
- **Content Pruning**: Dynamic filter (threshold 0.48).
- **Markdown**: Structured output with link flattening.

## Quick Start

1. **Start everything:**
   ```bash
   docker compose up -d
   ```

2. **Test SearXNG JSON:**
   ```bash
   curl "http://localhost:8080/search?q=test&format=json" | jq '.results[0:2]'
   ```

3. **Test MCP server:**
   ```bash
   npx @modelcontextprotocol/inspector http://localhost:8000/sse
   ```

## Running

### Docker Compose (Recommended)

Starts **both** SearXNG and MCP server:

```bash
docker compose up -d
```

**Override port/log level:**
```bash
PORT=9000 LOG_LEVEL=DEBUG docker compose up -d
```

## Testing with MCP Inspector

The **official MCP Inspector** is the easiest way to test the full MCP protocol:

```bash
# Install Node.js if needed, then:
npx @modelcontextprotocol/inspector http://localhost:8000/sse
```

This will:
1. Connect via SSE and establish session.
2. List available tools (`web_search`, `crawl_url`).
3. Let you invoke tools interactively with proper JSON-RPC framing.
4. Show real-time responses and debug info.

## Manual Docker

1. **SearXNG first:**
   ```bash
   docker run -d --name searxng -p 8080:8080 -v $(pwd)/searxng-settings.yml:/etc/searxng/settings.yml:ro searxng/searxng:latest
   ```

2. **MCP server:**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e SEARXNG_URL=http://host.docker.internal:8080 \
     --shm-size=2gb \
     --name web-search-mcp \
     web-search-mcp
   ```

3. **Test:**
   ```bash
   npx @modelcontextprotocol/inspector http://localhost:8000/sse
   ```

## Resource Requirements

| Resource | Recommended | Reason |
|----------|-------------|--------|
| **RAM** | **2 GB+** | Browsers + search aggregation. |
| **CPU** | **2 vCPUs** | Page rendering + search. |
| **Shared Mem** | **2 GB** | Chromium stability. |

## MCP Config

```json
{
  "mcpServers": {
    "web-search": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```