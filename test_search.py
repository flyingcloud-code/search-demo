import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入被测试的模块
from search import (
    classify_query,
    search_wikipedia,
    search_engine,
    search_category,
    format_results,
    browse_content
)


# 测试查询分类函数
class TestClassifyQuery:
    def test_academic_classification(self):
        assert classify_query("research paper on machine learning") == "academic"
        assert classify_query("latest study on climate change") == "academic"
        assert classify_query("neural network model comparison") == "academic"
    
    def test_knowledge_classification(self):
        assert classify_query("what is quantum computing") == "knowledge"
        assert classify_query("history of the internet") == "knowledge"
        assert classify_query("definition of blockchain") == "knowledge"
    
    def test_product_classification(self):
        assert classify_query("best gaming laptops 2023") == "product"
        assert classify_query("recommend smartphone under 500") == "product"
        assert classify_query("top server hardware for small business") == "product"
    
    def test_policy_classification(self):
        assert classify_query("latest tariff news") == "policy"
        assert classify_query("new policy on renewable energy") == "policy"
        assert classify_query("recent changes in trade regulations") == "policy"
    
    def test_general_classification(self):
        assert classify_query("weather forecast") == "general"
        assert classify_query("local restaurants") == "general"
        assert classify_query("current time in Tokyo") == "general"


# 测试Wikipedia搜索函数
class TestSearchWikipedia:
    @patch('search.wikipedia')
    def test_search_wikipedia_success(self, mock_wikipedia):
        # 模拟wikipedia.search返回结果
        mock_wikipedia.search.return_value = ["Artificial Intelligence", "Machine Learning"]
        
        # 模拟wikipedia.page返回结果
        mock_page1 = MagicMock()
        mock_page1.title = "Artificial Intelligence"
        mock_page1.url = "https://en.wikipedia.org/wiki/Artificial_Intelligence"
        mock_page1.summary = "Artificial intelligence (AI) is intelligence demonstrated by machines."
        
        mock_page2 = MagicMock()
        mock_page2.title = "Machine Learning"
        mock_page2.url = "https://en.wikipedia.org/wiki/Machine_Learning"
        mock_page2.summary = "Machine learning is a field of inquiry devoted to understanding and building methods."
        
        # 设置side_effect使第一次调用返回mock_page1，第二次调用返回mock_page2
        mock_wikipedia.page.side_effect = [mock_page1, mock_page2]
        
        # 调用被测试的函数
        results = search_wikipedia("artificial intelligence", max_results=2)
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["source"] == "Wikipedia"
        assert results[0]["title"] == "Artificial Intelligence"
        assert results[0]["link"] == "https://en.wikipedia.org/wiki/Artificial_Intelligence"
        assert "Artificial intelligence" in results[0]["snippet"]
        
        assert results[1]["source"] == "Wikipedia"
        assert results[1]["title"] == "Machine Learning"
        assert results[1]["link"] == "https://en.wikipedia.org/wiki/Machine_Learning"
        assert "Machine learning" in results[1]["snippet"]
    
    @patch('search.wikipedia')
    def test_search_wikipedia_disambiguation(self, mock_wikipedia):
        # 模拟wikipedia.search返回结果
        mock_wikipedia.search.return_value = ["Python"]
        
        # 模拟DisambiguationError异常
        disambiguation_error = mock_wikipedia.exceptions.DisambiguationError("Python", ["Python (programming language)", "Python (snake)"])
        
        # 设置side_effect使第一次调用抛出DisambiguationError，第二次调用返回mock_page
        mock_page = MagicMock()
        mock_page.title = "Python (programming language)"
        mock_page.url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        mock_page.summary = "Python is a high-level, general-purpose programming language."
        
        mock_wikipedia.page.side_effect = [disambiguation_error, mock_page]
        
        # 调用被测试的函数
        results = search_wikipedia("python", max_results=1)
        
        # 验证结果
        assert len(results) == 1
        assert results[0]["source"] == "Wikipedia"
        assert results[0]["title"] == "Python (programming language)"
        assert results[0]["link"] == "https://en.wikipedia.org/wiki/Python_(programming_language)"
        assert "Python is a high-level" in results[0]["snippet"]
    
    @patch('search.wikipedia')
    def test_search_wikipedia_empty_results(self, mock_wikipedia):
        # 模拟wikipedia.search返回空结果
        mock_wikipedia.search.return_value = []
        
        # 调用被测试的函数
        results = search_wikipedia("nonexistentquery12345", max_results=5)
        
        # 验证结果
        assert len(results) == 0
    
    @patch('search.wikipedia')
    def test_search_wikipedia_exception(self, mock_wikipedia):
        # 模拟wikipedia.search抛出异常
        mock_wikipedia.search.side_effect = Exception("API error")
        
        # 调用被测试的函数
        results = search_wikipedia("artificial intelligence", max_results=5)
        
        # 验证结果
        assert len(results) == 0


# 测试搜索引擎函数
class TestSearchEngine:
    @patch('search.DDGS')
    def test_search_engine_duckduckgo(self, mock_ddgs):
        # 模拟DDGS实例
        mock_ddgs_instance = MagicMock()
        mock_ddgs.return_value = mock_ddgs_instance
        
        # 模拟搜索结果
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
        mock_ddgs_instance.text.return_value = mock_results
        
        # 调用被测试的函数
        results = search_engine("test query", engine="duckduckgo", max_results=2)
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["source"] == "DuckDuckGo"
        assert results[0]["title"] == "Test Result 1"
        assert results[0]["link"] == "https://example.com/1"
        assert "This is the first test result" in results[0]["snippet"]
        
        assert results[1]["source"] == "DuckDuckGo"
        assert results[1]["title"] == "Test Result 2"
        assert results[1]["link"] == "https://example.com/2"
        assert "This is the second test result" in results[1]["snippet"]
    
    @patch('search.google_search')
    def test_search_engine_google(self, mock_google_search):
        # 模拟google_search返回结果
        mock_google_search.return_value = [
            "https://example.com/1",
            "https://example.com/2"
        ]
        
        # 调用被测试的函数
        results = search_engine("test query", engine="google", max_results=2)
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["source"] == "Google"
        assert results[0]["link"] == "https://example.com/1"
        assert results[1]["source"] == "Google"
        assert results[1]["link"] == "https://example.com/2"
    
    @patch('search.DDGS')
    def test_search_engine_with_site_qualifier(self, mock_ddgs):
        # 模拟DDGS实例
        mock_ddgs_instance = MagicMock()
        mock_ddgs.return_value = mock_ddgs_instance
        
        # 模拟搜索结果
        mock_results = [
            {
                "title": "Example Site Result",
                "href": "https://example.com/result",
                "body": "This is a result from example.com domain."
            }
        ]
        mock_ddgs_instance.text.return_value = mock_results
        
        # 调用被测试的函数，使用site限定词
        results = search_engine("test query", engine="duckduckgo", site="example.com", max_results=1)
        
        # 验证结果
        assert len(results) == 1
        assert results[0]["source"] == "DuckDuckGo"
        assert results[0]["title"] == "Example Site Result"
        assert results[0]["link"] == "https://example.com/result"
        
        # 验证DDGS.text被调用时使用了正确的参数
        mock_ddgs_instance.text.assert_called_once()
        call_args = mock_ddgs_instance.text.call_args[1]
        assert "site:example.com" in call_args["keywords"]


# 测试分类搜索函数
class TestSearchCategory:
    @patch('search.search_wikipedia')
    def test_search_category_knowledge(self, mock_search_wikipedia):
        # 模拟search_wikipedia返回结果
        mock_results = [
            {
                "source": "Wikipedia",
                "title": "Test Knowledge",
                "link": "https://en.wikipedia.org/wiki/Test_Knowledge",
                "snippet": "This is a test knowledge snippet."
            }
        ]
        mock_search_wikipedia.return_value = mock_results
        
        # 调用被测试的函数
        results = search_category("knowledge", "test knowledge", max_results=1)
        
        # 验证结果
        assert len(results) == 1
        assert results[0]["source"] == "Wikipedia"
        assert results[0]["title"] == "Test Knowledge"
        
        # 验证search_wikipedia被调用
        mock_search_wikipedia.assert_called_once_with("test knowledge", 1, False)
    
    @patch('search.search_engine')
    def test_search_category_general(self, mock_search_engine):
        # 模拟search_engine返回结果
        mock_results = [
            {
                "source": "DuckDuckGo",
                "title": "General Result",
                "link": "https://example.com/general",
                "snippet": "This is a general search result."
            }
        ]
        mock_search_engine.return_value = mock_results
        
        # 调用被测试的函数
        results = search_category("general", "general query", max_results=1)
        
        # 验证结果
        assert len(results) == 1
        assert results[0]["source"] == "DuckDuckGo"
        assert results[0]["title"] == "General Result"
        
        # 验证search_engine被调用
        mock_search_engine.assert_called_once_with("general query", "duckduckgo", max_results=1, verbose=False)


# 测试结果格式化函数
class TestFormatResults:
    @patch('search.browse_content')
    def test_format_results_json(self, mock_browse_content):
        # 准备测试数据
        test_results = [
            {
                "source": "Test Source",
                "title": "Test Title",
                "link": "https://example.com/test",
                "snippet": "Test snippet content."
            }
        ]
        
        # 调用被测试的函数
        output = format_results(test_results, "json", 1)
        
        # 验证结果是有效的JSON
        parsed = json.loads(output)
        assert len(parsed) == 1
        assert parsed[0]["source"] == "Test Source"
        assert parsed[0]["title"] == "Test Title"
        assert parsed[0]["link"] == "https://example.com/test"
        assert parsed[0]["snippet"] == "Test snippet content."
        
        # 验证browse_content没有被调用（JSON格式不需要获取内容）
        mock_browse_content.assert_not_called()
    
    @patch('search.browse_content')
    def test_format_results_markdown(self, mock_browse_content):
        # 模拟browse_content返回结果
        mock_browse_content.return_value = "Browsed content for test."
        
        # 准备测试数据
        test_results = [
            {
                "source": "Test Source",
                "title": "Test Title",
                "link": "https://example.com/test",
                "snippet": "Test snippet content."
            }
        ]
        
        # 调用被测试的函数
        output = format_results(test_results, "markdown", 1)
        
        # 验证结果是Markdown格式
        assert "# 搜索结果" in output
        assert "## 1. Test Title" in output
        assert "**来源**: Test Source" in output
        assert "**链接**: [https://example.com/test](https://example.com/test)" in output
        assert "**摘要**: Test snippet content." in output
        assert "**内容**: Browsed content for test." in output
        
        # 验证browse_content被调用
        mock_browse_content.assert_called_once_with("https://example.com/test", False)


# 测试内容浏览函数
class TestBrowseContent:
    @patch('search.requests.get')
    def test_browse_content_success(self, mock_get):
        # 模拟requests.get返回结果
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Test paragraph 1.</p><p>Test paragraph 2.</p></body></html>"
        mock_get.return_value = mock_response
        
        # 调用被测试的函数
        content = browse_content("https://example.com/test")
        
        # 验证结果
        assert content == "Test paragraph 1. Test paragraph 2."
        
        # 验证requests.get被调用
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0] == "https://example.com/test"
    
    @patch('search.requests.get')
    def test_browse_content_exception(self, mock_get):
        # 模拟requests.get抛出异常
        mock_get.side_effect = Exception("Connection error")
        
        # 调用被测试的函数
        content = browse_content("https://example.com/test")
        
        # 验证结果
        assert content == "获取内容失败"
        
        # 验证requests.get被调用
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0] == "https://example.com/test"


if __name__ == "__main__":
    pytest.main(['-v', __file__])