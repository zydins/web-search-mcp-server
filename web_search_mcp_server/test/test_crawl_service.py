import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from crawl_service import perform_crawl, flatten_markdown_links


class TestFlattenMarkdownLinks:
    """Test suite for flatten_markdown_links function"""

    def test_flatten_simple_link(self):
        """Test flattening a simple markdown link"""
        text = "[Link Text](https://example.com)"
        result = flatten_markdown_links(text)
        assert result == "Link Text"

    def test_flatten_image_link(self):
        """Test flattening an image markdown"""
        text = "![Alt Text](https://example.com/image.png)"
        result = flatten_markdown_links(text)
        assert result == "Alt Text"

    def test_flatten_nested_links(self):
        """Test flattening nested markdown structures"""
        text = "[![Image Alt](img.png)](https://example.com)"
        result = flatten_markdown_links(text)
        assert result == "Image Alt"

    def test_flatten_multiple_links(self):
        """Test flattening multiple links in text"""
        text = "Check [this link](url1) and [that link](url2)"
        result = flatten_markdown_links(text)
        assert result == "Check this link and that link"

    def test_flatten_empty_text(self):
        """Test handling of empty text"""
        assert flatten_markdown_links("") == ""
        assert flatten_markdown_links(None) == ""

    def test_flatten_no_links(self):
        """Test text without links remains unchanged"""
        text = "Plain text without links"
        result = flatten_markdown_links(text)
        assert result == text

    def test_flatten_complex_nested(self):
        """Test complex nested structures"""
        text = "Text with [link with ![nested image](img.png) inside](url)"
        result = flatten_markdown_links(text)
        # Should recursively flatten
        assert "(" not in result and ")" not in result


class TestPerformCrawl:
    """Test suite for perform_crawl function"""

    @pytest.mark.asyncio
    async def test_successful_crawl_small_content(self):
        """Test successful crawl with content under threshold"""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.markdown = "# Header\n\n[Link](url) and ![image](img.png)"

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None

        with patch('crawl_service.AsyncWebCrawler', return_value=mock_crawler):
            result = await perform_crawl("https://example.com")

            assert "Header" in result
            assert "Link" in result
            assert "image" in result
            assert "url" not in result.lower() or result == "# Header\n\nLink and image"

    @pytest.mark.asyncio
    async def test_successful_crawl_large_content(self):
        """Test successful crawl with content over threshold"""
        large_content = "a" * 15000
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.markdown = large_content

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None

        with patch('crawl_service.AsyncWebCrawler', return_value=mock_crawler):
            result = await perform_crawl("https://example.com")

            assert len(result) == 10000
            assert result == "a" * 10000

    @pytest.mark.asyncio
    async def test_crawl_failure(self):
        """Test handling of crawl failure"""
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error_message = "Connection timeout"

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None

        with patch('crawl_service.AsyncWebCrawler', return_value=mock_crawler):
            result = await perform_crawl("https://example.com")

            assert "Crawl failed" in result
            assert "Connection timeout" in result

    @pytest.mark.asyncio
    async def test_crawl_with_empty_markdown(self):
        """Test crawl with empty markdown content"""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.markdown = ""

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None

        with patch('crawl_service.AsyncWebCrawler', return_value=mock_crawler):
            result = await perform_crawl("https://example.com")

            assert result == ""

    @pytest.mark.asyncio
    async def test_crawl_exactly_at_threshold(self):
        """Test crawl with content exactly at threshold"""
        content_at_threshold = "b" * 10000
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.markdown = content_at_threshold

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None

        with patch('crawl_service.AsyncWebCrawler', return_value=mock_crawler):
            result = await perform_crawl("https://example.com")

            assert len(result) == 10000

    @pytest.mark.asyncio
    async def test_crawl_config_parameters(self):
        """Test that crawler is called with correct config"""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.markdown = "test"

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None

        with patch('crawl_service.AsyncWebCrawler', return_value=mock_crawler):
            await perform_crawl("https://example.com")

            mock_crawler.arun.assert_called_once()
            call_args = mock_crawler.arun.call_args
            assert call_args[1]["url"] == "https://example.com"
            assert "config" in call_args[1]
