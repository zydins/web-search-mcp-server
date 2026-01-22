import re
import logging
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Configure logger
logger = logging.getLogger(__name__)

def flatten_markdown_links(text):
    """
    Robustly removes markdown links/images while keeping the text/alt-text.
    """
    if not text:
        return ""
    
    prev_text = None
    while text != prev_text:
        prev_text = text
        text = re.sub(r'!?(?:\[((?:[^\[\]]|!\[[^\]]*\]\([^\)]+\))*)\])\([^\)]+\)', r'\1', text)
        
    return text

async def perform_crawl(url: str) -> str:
    logger.info(f"Starting crawl for: {url}")

    pruning_filter = PruningContentFilter(
        threshold=0.48,
        threshold_type="dynamic",
        min_word_threshold=5
    )

    md_generator = DefaultMarkdownGenerator(
        content_filter=pruning_filter
    )

    config = CrawlerRunConfig(
        word_count_threshold=200,
        only_text=True,
        markdown_generator=md_generator
    )

    logger.info("Launching crawler...")
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            config=config
        )

        if result.success:
            logger.info("Crawl success! Processing markdown...")
            raw_markdown = result.markdown
            clean_text = flatten_markdown_links(raw_markdown)
            logger.info(f"Returning {len(clean_text)} chars of text")
            return clean_text
        else:
            logger.error(f"Crawl failed: {result.error_message}")
            return f"Crawl failed: {result.error_message}"
