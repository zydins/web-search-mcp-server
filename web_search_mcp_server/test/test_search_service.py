import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from search_service import perform_web_search


class TestPerformWebSearch:
    """Test suite for perform_web_search function"""

    @pytest.mark.asyncio
    async def test_successful_search_with_results(self):
        """Test successful search returning multiple results"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Result 1", "url": "https://example1.com"},
                {"title": "Result 2", "url": "https://example2.com"},
                {"title": "Result 3", "url": "https://example3.com"},
            ]
        }

        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            result = await perform_web_search("test query")

            result_data = json.loads(result)
            assert "results" in result_data
            assert len(result_data["results"]) == 3
            assert result_data["results"][0]["title"] == "Result 1"
            assert result_data["results"][0]["url"] == "https://example1.com"

            mock_instance.get.assert_called_once()
            call_args = mock_instance.get.call_args
            assert call_args[0][0] == "http://localhost:8080/search"
            assert call_args[1]["params"]["q"] == "test query"
            assert call_args[1]["params"]["format"] == "json"

    @pytest.mark.asyncio
    async def test_successful_search_limits_to_three_results(self):
        """Test that only top 3 results are returned even if more exist"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": f"Result {i}", "url": f"https://example{i}.com"}
                for i in range(10)
            ]
        }

        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            result = await perform_web_search("test query")

            result_data = json.loads(result)
            assert len(result_data["results"]) == 3

    @pytest.mark.asyncio
    async def test_search_with_no_results(self):
        """Test search that returns no results"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}

        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            result = await perform_web_search("nonexistent query")

            result_data = json.loads(result)
            assert result_data == {"results": []}

    @pytest.mark.asyncio
    async def test_search_with_missing_results_key(self):
        """Test search response without results key"""
        mock_response = MagicMock()
        mock_response.json.return_value = {}

        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            result = await perform_web_search("test query")

            result_data = json.loads(result)
            assert result_data == {"results": []}

    @pytest.mark.asyncio
    async def test_search_with_missing_title_and_url(self):
        """Test handling of results with missing title/url fields"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {},
                {"title": "Only Title"},
                {"url": "https://only-url.com"}
            ]
        }

        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            result = await perform_web_search("test query")

            result_data = json.loads(result)
            assert len(result_data["results"]) == 3
            assert result_data["results"][0]["title"] == "No Title"
            assert result_data["results"][0]["url"] == ""
            assert result_data["results"][1]["title"] == "Only Title"
            assert result_data["results"][1]["url"] == ""
            assert result_data["results"][2]["url"] == "https://only-url.com"

    @pytest.mark.asyncio
    async def test_search_http_error(self):
        """Test handling of HTTP errors"""
        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = httpx.HTTPStatusError(
                "500 Server Error", 
                request=MagicMock(), 
                response=MagicMock()
            )
            mock_client.return_value = mock_instance

            result = await perform_web_search("test query")

            result_data = json.loads(result)
            assert "error" in result_data

    @pytest.mark.asyncio
    async def test_search_timeout_error(self):
        """Test handling of timeout errors"""
        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = httpx.TimeoutException("Timeout")
            mock_client.return_value = mock_instance

            result = await perform_web_search("test query")

            result_data = json.loads(result)
            assert "error" in result_data

    @pytest.mark.asyncio
    async def test_search_generic_exception(self):
        """Test handling of generic exceptions"""
        with patch('search_service.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = Exception("Generic error")
            mock_client.return_value = mock_instance

            result = await perform_web_search("test query")

            result_data = json.loads(result)
            assert "error" in result_data
            assert "Generic error" in result_data["error"]

    @pytest.mark.asyncio
    async def test_custom_searxng_url(self):
        """Test using custom SEARXNG_URL from environment"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}

        with patch('search_service.httpx.AsyncClient') as mock_client, patch.dict('os.environ', {'SEARXNG_URL': 'http://custom:9090'}):

            # Reload module to pick up new env var
            import importlib
            import search_service
            importlib.reload(search_service)

            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_client.return_value = mock_instance

            result = await search_service.perform_web_search("test")

            call_args = mock_instance.get.call_args
            assert "http://custom:9090/search" in call_args[0][0]
