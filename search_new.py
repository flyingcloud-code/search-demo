import argparse
import json
import time
import random
from datetime import datetime
import arxiv
import wikipedia
from duckduckgo_search import DDGS
from googlesearch import search as google_search
import re
import requests
from bs4 import BeautifulSoup

class SearchEngine:
    """搜索引擎抽象基类"""
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def search(self, query, max_results=5, format='json', **kwargs):
        """搜索方法，子类必须实现
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            format: 输出格式，支持'json'、'markdown'、'html'
            **kwargs: 其他搜索参数
        """
        results = self._search_impl(query, max_results, **kwargs)
        return self._format_results(results, format)
    
    def _search_impl(self, query, max_results, **kwargs):
        """实际搜索实现，子类必须实现"""
        raise NotImplementedError
    
    def _format_results(self, results, format):
        """格式化搜索结果"""
        if format == 'json':
            return json.dumps(results, indent=2, ensure_ascii=False)
        elif format == 'markdown':
            return self._to_markdown(results)
        elif format == 'html':
            return self._to_html(results)
        else:
            return results
    
    def _to_markdown(self, results):
        """转换为Markdown格式"""
        output = []
        for result in results:
            output.append(f"### {result['title']}\n")
            output.append(f"- 来源: {result['source']}\n")
            output.append(f"- 链接: [{result['link']}]({result['link']})\n")
            output.append(f"- 摘要: {result['snippet']}\n\n")
        return '\n'.join(output)
    
    def _to_html(self, results):
        """转换为HTML格式"""
        output = ['<div class="search-results">']
        for result in results:
            output.append(f"<div class='result'>")
            output.append(f"<h3>{result['title']}</h3>")
            output.append(f"<p><strong>来源:</strong> {result['source']}</p>")
            output.append(f"<p><strong>链接:</strong> <a href='{result['link']}'>{result['link']}</a></p>")
            output.append(f"<p><strong>摘要:</strong> {result['snippet']}</p>")
            output.append("</div>")
        output.append("</div>")
        return '\n'.join(output)

class ArxivSearchEngine(SearchEngine):
    """arXiv搜索引擎实现"""
    def _search_impl(self, query, max_results=5, **kwargs):
        if self.verbose:
            print(f"\n[arXiv] 开始搜索: {query}")
        try:
            search = arxiv.Search(query=query, max_results=max_results, 
                                sort_by=arxiv.SortCriterion.SubmittedDate)
            results = []
            for paper in search.results():
                results.append({
                    "source": "arXiv",
                    "title": paper.title,
                    "link": paper.entry_id,
                    "snippet": paper.summary[:200]
                })
            return results
        except Exception as e:
            print(f"arXiv 搜索错误: {e}")
            return []

class WikipediaSearchEngine(SearchEngine):
    """Wikipedia搜索引擎实现"""
    def __init__(self, verbose=False, lang='en'):
        super().__init__(verbose)
        self.lang = lang
        wikipedia.set_lang(lang)
    
    def _search_impl(self, query, max_results=5, **kwargs):
        if self.verbose:
            print(f"\n[Wikipedia] 开始搜索: {query}")
        try:
            search_results = wikipedia.search(query, results=max_results)
            results = []
            for title in search_results[:max_results]:
                try:
                    page = wikipedia.page(title)
                    results.append({
                        "source": "Wikipedia",
                        "title": page.title,
                        "link": page.url,
                        "snippet": page.summary[:200]
                    })
                except Exception:
                    continue
            return results
        except Exception as e:
            print(f"Wikipedia 搜索错误: {e}")
            return []

class DuckDuckGoSearchEngine(SearchEngine):
    """DuckDuckGo搜索引擎实现"""
    def parse_qualifiers(self, query, **kwargs):
        """处理Google搜索限定词: 精确短语、排除词、分组、URL/标题/正文限定、时间范围等"""
        qualifiers = {
            'exact_phrase': kwargs.get('exact_phrase'),
            'exclude': kwargs.get('exclude'),
            'filetype': kwargs.get('filetype'),
            'site': kwargs.get('site'),
            'intitle': kwargs.get('intitle'),
            'inurl': kwargs.get('inurl'),
            'intext': kwargs.get('intext'),
            'allintitle': kwargs.get('allintitle'),
            'allinurl': kwargs.get('allinurl'),
            'allintext': kwargs.get('allintext'),
            'before': kwargs.get('before'),
            'after': kwargs.get('after'),
            'group': kwargs.get('group'),
            'or_terms': kwargs.get('or_terms')
        }
        
        # 精确短语
        if qualifiers['exact_phrase']:
            query = f'"{qualifiers["exact_phrase"]}"'
        
        # 排除词
        if qualifiers['exclude']:
            query += f" -{qualifiers['exclude']}"
        
        # 文件类型
        if qualifiers['filetype']:
            query += f" filetype:{qualifiers['filetype']}"
        
        # 站点限定
        if qualifiers['site']:
            query += f" site:{qualifiers['site']}"
        
        # 标题/URL/正文限定
        if qualifiers['intitle']:
            query += f" intitle:{qualifiers['intitle']}"
        if qualifiers['inurl']:
            query += f" inurl:{qualifiers['inurl']}"
        if qualifiers['intext']:
            query += f" intext:{qualifiers['intext']}"
        
        # 多条件限定
        if qualifiers['allintitle']:
            query += f" allintitle:{qualifiers['allintitle']}"
        if qualifiers['allinurl']:
            query += f" allinurl:{qualifiers['allinurl']}"
        if qualifiers['allintext']:
            query += f" allintext:{qualifiers['allintext']}"
        
        # 时间范围
        if qualifiers['before']:
            query += f" before:{qualifiers['before']}"
        if qualifiers['after']:
            query += f" after:{qualifiers['after']}"
        
        # 分组和OR条件
        if qualifiers['group']:
            query = f"({query})"
        if qualifiers['or_terms']:
            query += f" OR {qualifiers['or_terms']}"
            
        return query
    
    def _search_impl(self, query, max_results=5, **kwargs):
        if self.verbose:
            print(f"\n[DuckDuckGo] 开始搜索: {query}")
        try:
            query = self.parse_qualifiers(query, **kwargs)
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        "source": "DuckDuckGo",
                        "title": result.get('title', ''),
                        "link": result.get('href', ''),
                        "snippet": result.get('body', '')[:200]
                    })
            return results
        except Exception as e:
            print(f"DuckDuckGo 搜索错误: {e}")
            return []

class GoogleSearchEngine(SearchEngine):
    """Google搜索引擎实现"""
    def parse_qualifiers(self, query, **kwargs):
        """处理Google搜索限定词: 精确短语、排除词、分组、URL/标题/正文限定、时间范围等"""
        qualifiers = {
            'exact_phrase': kwargs.get('exact_phrase'),
            'exclude': kwargs.get('exclude'),
            'filetype': kwargs.get('filetype'),
            'site': kwargs.get('site'),
            'intitle': kwargs.get('intitle'),
            'inurl': kwargs.get('inurl'),
            'intext': kwargs.get('intext'),
            'allintitle': kwargs.get('allintitle'),
            'allinurl': kwargs.get('allinurl'),
            'allintext': kwargs.get('allintext'),
            'before': kwargs.get('before'),
            'after': kwargs.get('after'),
            'group': kwargs.get('group'),
            'or_terms': kwargs.get('or_terms')
        }
        
        # 精确短语
        if qualifiers['exact_phrase']:
            query = f'"{qualifiers["exact_phrase"]}"'
        
        # 排除词
        if qualifiers['exclude']:
            query += f" -{qualifiers['exclude']}"
        
        # 文件类型
        if qualifiers['filetype']:
            query += f" filetype:{qualifiers['filetype']}"
        
        # 站点限定
        if qualifiers['site']:
            query += f" site:{qualifiers['site']}"
        
        # 标题/URL/正文限定
        if qualifiers['intitle']:
            query += f" intitle:{qualifiers['intitle']}"
        if qualifiers['inurl']:
            query += f" inurl:{qualifiers['inurl']}"
        if qualifiers['intext']:
            query += f" intext:{qualifiers['intext']}"
        
        # 多条件限定
        if qualifiers['allintitle']:
            query += f" allintitle:{qualifiers['allintitle']}"
        if qualifiers['allinurl']:
            query += f" allinurl:{qualifiers['allinurl']}"
        if qualifiers['allintext']:
            query += f" allintext:{qualifiers['allintext']}"
        
        # 时间范围
        if qualifiers['before']:
            query += f" before:{qualifiers['before']}"
        if qualifiers['after']:
            query += f" after:{qualifiers['after']}"
        
        # 分组和OR条件
        if qualifiers['group']:
            query = f"({query})"
        if qualifiers['or_terms']:
            query += f" OR {qualifiers['or_terms']}"
            
        return query
    
    def _search_impl(self, query, max_results=5, **kwargs):
        if self.verbose:
            print(f"\n[Google] 开始搜索: {query}")
        try:
            query = self.parse_qualifiers(query, **kwargs)
            results = []
            for url in google_search(query, num_results=max_results):
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else url
                    results.append({
                        "source": "Google",
                        "title": title,
                        "link": url,
                        "snippet": soup.get_text()[:200]
                    })
                except Exception:
                    continue
            return results
        except Exception as e:
            print(f"Google 搜索错误: {e}")
            return []

class SearchManager:
    """搜索管理类"""
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.engines = {
            "arxiv": ArxivSearchEngine(verbose),
            "wikipedia": WikipediaSearchEngine(verbose),
            "duckduckgo": DuckDuckGoSearchEngine(verbose),
            "google": GoogleSearchEngine(verbose),
        }
    
    def search(self, query, category=None, max_results=5, **kwargs):
        """根据分类执行搜索"""
        if category and category in self.engines:
            return self.engines[category].search(query, max_results, **kwargs)
        return []

if __name__ == "__main__":
    # 示例用法
    manager = SearchManager(verbose=True)
    
    # 基本搜索测试
    print("\n=== 基本搜索测试 ===")
    results = manager.search("machine learning", category="wikipedia", max_results=2)
    print(json.dumps(results, indent=2))
    
    # Google限定词测试
    print("\n=== Google限定词测试 ===")
    # 精确短语搜索
    print("\n1. 精确短语搜索:")
    results = manager.search("machine learning", category="google", exact_phrase="deep learning", max_results=2)
    print(json.dumps(results, indent=2))
    
    # 排除词搜索
    print("\n2. 排除词搜索:")
    results = manager.search("machine learning", category="google", exclude="neural", max_results=2)
    print(json.dumps(results, indent=2))
    
    # 站点限定搜索
    print("\n3. 站点限定搜索:")
    results = manager.search("machine learning", category="google", site="wikipedia.org", max_results=2)
    print(json.dumps(results, indent=2))
    
    # DuckDuckGo限定词测试
    print("\n=== DuckDuckGo限定词测试 ===")
    # 文件类型搜索
    print("\n1. 文件类型搜索:")
    results = manager.search("machine learning", category="duckduckgo", filetype="pdf", max_results=2)
    print(json.dumps(results, indent=2))
    
    # 标题限定搜索
    print("\n2. 标题限定搜索:")
    results = manager.search("machine learning", category="duckduckgo", intitle="introduction", max_results=2)
    print(json.dumps(results, indent=2))
    
    # 时间范围搜索
    print("\n3. 时间范围搜索:")
    results = manager.search("machine learning", category="duckduckgo", after="2023-01-01", max_results=2)
    print(json.dumps(results, indent=2))