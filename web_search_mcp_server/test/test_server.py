import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from server import web_search, crawl_url


class TestWebSearch:
    """Test suite for web_search tool"""

    @pytest.mark.asyncio
    async def test_web_search_calls_perform_web_search(self):
        """Test that web_search calls perform_web_search correctly"""
        expected_result = '{"results": [{"title": "Test", "url": "https://test.com"}]}'

        with patch('server.perform_web_search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = expected_result

            result = await web_search("test query")

            assert result == expected_result
            mock_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_web_search_with_empty_query(self):
        """Test web_search with empty query string"""
        with patch('server.perform_web_search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = '{"results": []}'

            result = await web_search("")

            mock_search.assert_called_once_with("")

    @pytest.mark.asyncio
    async def test_web_search_with_special_characters(self):
        """Test web_search with special characters in query"""
        query = "test & query <> special"

        with patch('server.perform_web_search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = '{"results": []}'

            result = await web_search(query)

            mock_search.assert_called_once_with(query)


class TestCrawlUrl:
    """Test suite for crawl_url tool"""

    @pytest.mark.asyncio
    async def test_crawl_url_calls_perform_crawl(self):
        """Test that crawl_url calls perform_crawl correctly"""
        expected_result = "# Page Title\n\nPage content"

        with patch('server.perform_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = expected_result

            result = await crawl_url("https://example.com")

            assert result == expected_result
            mock_crawl.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_crawl_url_with_http(self):
        """Test crawl_url with http URL"""
        with patch('server.perform_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = "content"

            result = await crawl_url("http://example.com")

            mock_crawl.assert_called_once_with("http://example.com")

    @pytest.mark.asyncio
    async def test_crawl_url_with_https(self):
        """Test crawl_url with https URL"""
        with patch('server.perform_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = "content"

            result = await crawl_url("https://example.com")

            mock_crawl.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_crawl_url_with_complex_url(self):
        """Test crawl_url with complex URL including path and query params"""
        url = "https://example.com/path/to/page?param=value&other=123"

        with patch('server.perform_crawl', new_callable=AsyncMock) as mock_crawl:
            mock_crawl.return_value = "content"

            result = await crawl_url(url)

            mock_crawl.assert_called_once_with(url)
