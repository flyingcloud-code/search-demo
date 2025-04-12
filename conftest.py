import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def mock_wikipedia():
    """提供模拟的Wikipedia API响应"""
    with patch('search.wikipedia') as mock:
        # 设置基本的搜索结果
        mock.search.return_value = ["Artificial Intelligence", "Machine Learning"]
        
        # 创建模拟页面对象
        mock_page1 = MagicMock()
        mock_page1.title = "Artificial Intelligence"
        mock_page1.url = "https://en.wikipedia.org/wiki/Artificial_Intelligence"
        mock_page1.summary = "Artificial intelligence (AI) is intelligence demonstrated by machines."
        
        mock_page2 = MagicMock()
        mock_page2.title = "Machine Learning"
        mock_page2.url = "https://en.wikipedia.org/wiki/Machine_Learning"
        mock_page2.summary = "Machine learning is a field of inquiry devoted to understanding and building methods."
        
        # 设置page方法的返回值
        mock.page.side_effect = [mock_page1, mock_page2]
        
        yield mock

@pytest.fixture
def mock_ddgs():
    """提供模拟的DuckDuckGo搜索响应"""
    with patch('search.DDGS') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        # 设置模拟搜索结果
        mock_results = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "This is the first test result with some content."
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "This is the second test result with different content."
            }
        ]
        mock_instance.text.return_value = mock_results
        
        yield mock_class

@pytest.fixture
def mock_google_search():
    """提供模拟的Google搜索响应"""
    with patch('search.google_search') as mock:
        # 设置模拟搜索结果
        mock.return_value = [
            "https://example.com/1",
            "https://example.com/2"
        ]
        
        yield mock

@pytest.fixture
def mock_requests_get():
    """提供模拟的HTTP请求响应"""
    with patch('search.requests.get') as mock:
        # 创建模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Test paragraph 1.</p><p>Test paragraph 2.</p></body></html>"
        mock.return_value = mock_response
        
        yield mock

@pytest.fixture
def sample_search_results():
    """提供样本搜索结果数据"""
    return [
        {
            "source": "Test Source 1",
            "title": "Test Title 1",
            "link": "https://example.com/test1",
            "snippet": "Test snippet content 1."
        },
        {
            "source": "Test Source 2",
            "title": "Test Title 2",
            "link": "https://example.com/test2",
            "snippet": "Test snippet content 2."
        }
    ]