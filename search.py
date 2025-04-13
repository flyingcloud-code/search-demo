import argparse
import json
import time
import random
from datetime import datetime
import arxiv
# 导入wikipedia库
import wikipedia
from duckduckgo_search import DDGS
from googlesearch import search as google_search  # Google 搜索库
import re
import requests
from bs4 import BeautifulSoup

# 分类资源映射
CATEGORY_RESOURCES = {
    "academic": ["arXiv", "Google Scholar"],
    "knowledge": ["Wikipedia"],
    "product": ["TechRadar", "CNET", "Reddit"],
    "policy": ["USTR", "Reuters"],
    "general": ["DuckDuckGo", "Google"]
}

# 支持的限定词
QUALIFIERS = [
    "site:", "filetype:", "inurl:", "intitle:", "intext:",
    "allinurl:", "allintitle:", "allintext:", "before:", "after:"
]

def classify_query(query):
    """简单分类查询类型"""
    query = query.lower()
    if any(k in query for k in ["research", "paper", "academic", "study", "model"]):
        return "academic"
    elif any(k in query for k in ["history", "definition", "what is"]):
        return "knowledge"
    elif any(k in query for k in ["best", "recommend", "laptop", "server", "product"]):
        return "product"
    elif any(k in query for k in ["policy", "tariff", "news", "latest", "regulations", "changes", "trade"]):
        return "policy"
    return "general"

def search_arxiv(query, max_results=5, verbose=False):
    """使用 arxiv 库搜索"""
    if verbose:
        print(f"\n[arXiv] 开始搜索: {query}")
        print(f"[arXiv] 参数: max_results={max_results}, sort_by=SubmittedDate")
    try:
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
        if verbose:
            print(f"[arXiv] 搜索对象创建成功，开始获取结果...")
        results = []
        for i, paper in enumerate(search.results()):
            if verbose:
                print(f"[arXiv] 处理结果 #{i+1}: {paper.title}")
            results.append({
                "source": "arXiv",
                "title": paper.title,
                "link": paper.entry_id,
                "snippet": paper.summary[:200]
            })
        if verbose:
            print(f"[arXiv] 搜索完成，获取到 {len(results)} 条结果")
        return results
    except Exception as e:
        print(f"arXiv 搜索错误: {e}")
        if verbose:
            print(f"[arXiv] 详细错误信息: {str(e)}")
        return []



def search_wikipedia(query, max_results=5, verbose=False):
    """使用 wikipedia 库搜索"""
    if verbose:
        print(f"\n[Wikipedia] 开始搜索: {query}")
        print(f"[Wikipedia] 参数: max_results={max_results}")
    try:
        # 设置Wikipedia语言
        wikipedia.set_lang('en')
        if verbose:
            print(f"[Wikipedia] 使用wikipedia库搜索: {query}")
        # 使用wikipedia.search方法获取搜索结果
        search_results = wikipedia.search(query, results=max_results)
        if verbose:
            print(f"[Wikipedia] 搜索结果数量: {len(search_results)}")
        
        results = []
        if verbose:
            print(f"[Wikipedia] 开始处理搜索结果...")
        for i, title in enumerate(search_results[:max_results]):
            if verbose:
                print(f"[Wikipedia] 处理结果 #{i+1}: {title}")
            try:
                # 获取页面详细信息
                page = wikipedia.page(title)
                if verbose:
                    print(f"[Wikipedia] 页面存在，提取信息: {title}")
                results.append({
                    "source": "Wikipedia",
                    "title": page.title,
                    "link": page.url,
                    "snippet": page.summary[:200]
                })
            except wikipedia.exceptions.DisambiguationError as e:
                # 处理消歧义页面
                if verbose:
                    print(f"[Wikipedia] 消歧义页面: {title}, 选项: {e.options[:3]}...")
                # 尝试使用第一个选项
                if e.options:
                    try:
                        first_option = e.options[0]
                        page = wikipedia.page(first_option)
                        results.append({
                            "source": "Wikipedia",
                            "title": first_option,
                            "link": page.url,
                            "snippet": page.summary[:200]
                        })
                    except Exception as inner_e:
                        if verbose:
                            print(f"[Wikipedia] 处理第一个选项时出错: {str(inner_e)}")
            except Exception as e:
                if verbose:
                    print(f"[Wikipedia] 获取页面 {title} 时出错: {str(e)}")
        if verbose:
            print(f"[Wikipedia] 搜索完成，获取到 {len(results)} 条结果")
        return results
    except Exception as e:
        print(f"Wikipedia 搜索错误: {e}")
        if verbose:
            print(f"[Wikipedia] 详细错误信息: {str(e)}")
        return []

def search_scholar(query, max_results=5, verbose=False):
    """使用 scholarly 搜索"""
    if verbose:
        print(f"\n[Google Scholar] 开始搜索: {query}")
        print(f"[Google Scholar] 参数: max_results={max_results}")
    try:
        # 尝试导入和初始化scholarly
        try:
            if verbose:
                print(f"[Google Scholar] 尝试导入scholarly模块...")
            from scholarly import scholarly
            # 设置超时，防止无限等待
            import socket
            if verbose:
                print(f"[Google Scholar] 设置网络超时为10秒...")
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(10)  # 10秒超时
            try:
                if verbose:
                    print(f"[Google Scholar] 执行搜索查询: {query}")
                search_query = scholarly.search_pubs(query)
                if verbose:
                    print(f"[Google Scholar] 搜索查询创建成功")
            finally:
                if verbose:
                    print(f"[Google Scholar] 恢复原始网络超时设置")
                socket.setdefaulttimeout(original_timeout)  # 恢复原始超时设置
        except Exception as e:
            print(f"Google Scholar 初始化错误: {e}")
            if verbose:
                print(f"[Google Scholar] 初始化详细错误: {str(e)}")
            return []
            
        results = []
        if verbose:
            print(f"[Google Scholar] 开始处理搜索结果...")
        for i, pub in enumerate(search_query):
            if i >= max_results:
                if verbose:
                    print(f"[Google Scholar] 已达到最大结果数量限制: {max_results}")
                break
            if verbose:
                title = pub.get("bib", {}).get("title", "无标题")
                print(f"[Google Scholar] 处理结果 #{i+1}: {title}")
            results.append({
                "source": "Google Scholar",
                "title": pub.get("bib", {}).get("title", "无标题"),
                "link": pub.get("eprint_url", pub.get("pub_url", "无链接")),
                "snippet": pub.get("bib", {}).get("abstract", "无摘要")[:200]
            })
        if verbose:
            print(f"[Google Scholar] 搜索完成，获取到 {len(results)} 条结果")
        return results
    except Exception as e:
        print(f"Google Scholar 搜索错误: {e}")
        if verbose:
            print(f"[Google Scholar] 详细错误信息: {str(e)}")
        return []

def search_engine(query, engine="google", site=None, filetype=None, inurl=None, intitle=None, intext=None,
                 allinurl=None, allintitle=None, allintext=None, before=None, after=None, max_results=5, verbose=False):
    """通用搜索，支持 DuckDuckGo 和 Google"""
    if verbose:
        print(f"\n[搜索引擎] 开始搜索: {query}")
        print(f"[搜索引擎] 使用引擎: {engine}")
        print(f"[搜索引擎] 参数: max_results={max_results}")
        if any([site, filetype, inurl, intitle, intext, allinurl, allintitle, allintext, before, after]):
            print("[搜索引擎] 使用的限定词:")
            if site: print(f"  - site: {site}")
            if filetype: print(f"  - filetype: {filetype}")
            if inurl: print(f"  - inurl: {inurl}")
            if intitle: print(f"  - intitle: {intitle}")
            if intext: print(f"  - intext: {intext}")
            if allinurl: print(f"  - allinurl: {allinurl}")
            if allintitle: print(f"  - allintitle: {allintitle}")
            if allintext: print(f"  - allintext: {allintext}")
            if before: print(f"  - before: {before}")
            if after: print(f"  - after: {after}")
    
    results = []
    search_query = f'"{query}"'
    
    # 构建限定词
    if site:
        search_query += f" site:{site}"
    if filetype:
        search_query += f" filetype:{filetype}"
    if inurl:
        search_query += f" inurl:{inurl}"
    if intitle:
        search_query += f" intitle:{intitle}"
    if intext:
        search_query += f" intext:{intext}"
    if allinurl:
        search_query += " ".join(f"inurl:{word}" for word in allinurl.split())
    if allintitle:
        search_query += " ".join(f"intitle:{word}" for word in allintitle.split())
    if allintext:
        search_query += " ".join(f"intext:{word}" for word in allintext.split())
        
    if verbose:
        print(f"[搜索引擎] 构建的搜索查询: {search_query}")
    
    if engine == "duckduckgo":
        try:
            if verbose:
                print(f"[DuckDuckGo] 初始化DDGS客户端...")
            ddgs = DDGS()
            if verbose:
                print(f"[DuckDuckGo] 执行搜索: {search_query}")
                print(f"[DuckDuckGo] 区域设置: wt-wt, 最大结果数: {max_results * 2}")
            raw_results = ddgs.text(keywords=search_query, region="wt-wt", max_results=max_results * 2)
            if verbose:
                print(f"[DuckDuckGo] 获取到原始结果，开始处理...")
                print(f"[DuckDuckGo] 开始处理日期过滤和结果格式化...")
            
            # 处理 before/after
            result_count = 0
            filtered_count = 0
            for result in raw_results:
                result_count += 1
                if verbose:
                    print(f"[DuckDuckGo] 处理结果 #{result_count}: {result.get('title', '无标题')[:30]}...")
                date_str = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", result.get("body", ""))
                pub_date = date_str.group(1) if date_str else None
                
                if before and pub_date and pub_date >= before:
                    if verbose:
                        print(f"[DuckDuckGo] 结果被过滤: 日期 {pub_date} 不早于 {before}")
                    filtered_count += 1
                    continue
                if after and pub_date and pub_date <= after:
                    if verbose:
                        print(f"[DuckDuckGo] 结果被过滤: 日期 {pub_date} 不晚于 {after}")
                    filtered_count += 1
                    continue
                
                if verbose:
                    print(f"[DuckDuckGo] 添加结果: {result.get('title', '无标题')[:30]}...")
                results.append({
                    "source": "DuckDuckGo",
                    "title": result.get("title", "无标题"),
                    "link": result.get("href", "无链接"),
                    "snippet": result.get("body", "无摘要")[:200]
                })
            if verbose:
                print(f"[DuckDuckGo] 处理完成: 总结果 {result_count}, 过滤 {filtered_count}, 保留 {len(results)}")
        except Exception as e:
            print(f"DuckDuckGo 搜索错误: {e}")
            if verbose:
                print(f"[DuckDuckGo] 详细错误信息: {str(e)}")
    
    elif engine == "google":
        try:
            if verbose:
                print(f"[Google] 开始执行搜索: {search_query}")
                print(f"[Google] 请求结果数量: {max_results * 2}")
            result_count = 0
            filtered_count = 0
            for result in google_search(search_query, num_results=max_results * 2):
                result_count += 1
                if verbose:
                    print(f"[Google] 处理结果 #{result_count}")
                # 处理 googlesearch-python 返回的字符串结果
                # 在新版本中，结果是字符串而不是对象
                if isinstance(result, str):
                    url = result
                    try:
                        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        title = soup.title.string if soup.title else "无标题"
                        description = soup.find("meta", attrs={"name": "description"})
                        description = description["content"][:200] if description else "无摘要"
                    except Exception:
                        title = "无标题"
                        description = "无摘要"
                    if verbose:
                        print(f"[Google] 结果为字符串格式: {url[:50]}...")
                else:
                    # 兼容旧版本的对象格式
                    url = getattr(result, 'url', result) if hasattr(result, 'url') else result
                    title = getattr(result, 'name', "无标题") if hasattr(result, 'name') else "无标题"
                    description = getattr(result, 'description', "无摘要") if hasattr(result, 'description') else "无摘要"
                    if verbose:
                        print(f"[Google] 结果为对象格式: {title[:30]}...")
                
                date_str = None  # googlesearch-python 不直接返回日期
                if before or after:
                    if verbose:
                        print(f"[Google] 需要日期过滤，尝试从页面提取日期信息: {url[:50]}...")
                    # 尝试从页面提取日期
                    try:
                        if verbose:
                            print(f"[Google] 发送HTTP请求获取页面内容...")
                        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        date_meta = soup.find("meta", {"name": "date"})
                        date_str = date_meta["content"] if date_meta else None
                        if verbose:
                            print(f"[Google] 提取到日期: {date_str if date_str else '未找到日期'}")
                    except Exception as e:
                        print(f"提取日期错误: {e}")
                        if verbose:
                            print(f"[Google] 日期提取详细错误: {str(e)}")
                        date_str = None
                
                if before and date_str and date_str >= before:
                    if verbose:
                        print(f"[Google] 结果被过滤: 日期 {date_str} 不早于 {before}")
                    filtered_count += 1
                    continue
                if after and date_str and date_str <= after:
                    if verbose:
                        print(f"[Google] 结果被过滤: 日期 {date_str} 不晚于 {after}")
                    filtered_count += 1
                    continue
                
                if verbose:
                    print(f"[Google] 添加结果: {title[:30]}...")
                results.append({
                    "source": "Google",
                    "title": title,
                    "link": url,
                    "snippet": description[:200]
                })
            if verbose:
                print(f"[Google] 搜索完成，等待1-2秒防止限制...")
                print(f"[Google] 处理完成: 总结果 {result_count}, 过滤 {filtered_count}, 保留 {len(results)}")
            time.sleep(random.uniform(1, 2))  # 防止 Google 限制
        except Exception as e:
            print(f"Google 搜索错误: {e}")
            if verbose:
                print(f"[Google] 详细错误信息: {str(e)}")
    
    if verbose:
        print(f"[搜索引擎] 返回结果数量: {min(len(results), max_results)}")
    return results[:max_results]

def search_category(category, query, max_results=5, engine="duckduckgo", verbose=False):
    """分类搜索：调用对应库"""
    if verbose:
        print(f"\n[分类搜索] 开始搜索类别: {category}")
        print(f"[分类搜索] 查询: {query}")
        print(f"[分类搜索] 参数: max_results={max_results}, engine={engine}")
    results = []
    
    if category == "academic":
        if verbose:
            print(f"[分类搜索] 学术类别: 使用arXiv搜索...")
        results.extend(search_arxiv(query, max_results, verbose))
        try:
            if verbose:
                print(f"[分类搜索] 学术类别: 使用Google Scholar搜索...")
            scholar_results = search_scholar(query, max_results, verbose)
            results.extend(scholar_results)
        except KeyboardInterrupt:
            print("Google Scholar 搜索被中断，跳过此搜索源")
            if verbose:
                print(f"[分类搜索] Google Scholar搜索被用户中断")
        except Exception as e:
            print(f"Google Scholar 搜索失败: {e}")
            if verbose:
                print(f"[分类搜索] Google Scholar搜索详细错误: {str(e)}")
    elif category == "knowledge":
        if verbose:
            print(f"[分类搜索] 知识类别: 使用Wikipedia搜索...")
        results.extend(search_wikipedia(query, max_results, verbose))
    elif category == "product":
        if verbose:
            print(f"[分类搜索] 产品类别: 搜索多个产品评测网站...")
        if verbose:
            print(f"[分类搜索] 产品类别: 搜索TechRadar...")
        results.extend(search_engine(query, engine, site="techradar.com", max_results=max_results//2, verbose=verbose))
        if verbose:
            print(f"[分类搜索] 产品类别: 搜索CNET...")
        results.extend(search_engine(query, engine, site="cnet.com", max_results=max_results//2, verbose=verbose))
        if verbose:
            print(f"[分类搜索] 产品类别: 搜索Reddit...")
        results.extend(search_engine(query, engine, site="reddit.com", max_results=max_results//2, verbose=verbose))
    elif category == "policy":
        if verbose:
            print(f"[分类搜索] 政策类别: 搜索政策和新闻网站...")
        if verbose:
            print(f"[分类搜索] 政策类别: 搜索USTR...")
        results.extend(search_engine(query, engine, site="ustr.gov", max_results=max_results//2, verbose=verbose))
        if verbose:
            print(f"[分类搜索] 政策类别: 搜索路透社...")
        results.extend(search_engine(query, engine, site="reuters.com", max_results=max_results//2, verbose=verbose))
    elif category == "general":
        if verbose:
            print(f"[分类搜索] 通用类别: 使用{engine}搜索...")
        results.extend(search_engine(query, engine, max_results=max_results, verbose=verbose))
    
    if verbose:
        print(f"[搜索引擎] 返回结果数量: {min(len(results), max_results)}")
    return results[:max_results]

def browse_content(url, verbose=False):
    """浏览结果内容：提取摘要或前 200 字"""
    if verbose:
        print(f"[浏览内容] 开始获取URL内容: {url}")
    try:
        if verbose:
            print(f"[浏览内容] 发送HTTP请求...")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if verbose:
            print(f"[浏览内容] 状态码: {response.status_code}, 内容长度: {len(response.text)}字节")
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.select('p')
        if verbose:
            print(f"[浏览内容] 找到{len(paragraphs)}个段落")
        content = " ".join(p.text for p in paragraphs if p.text.strip())[:200]
        if verbose:
            print(f"[浏览内容] 提取内容长度: {len(content)}字符")
        return content or "无内容"
    except Exception as e:
        if verbose:
            print(f"[浏览内容] 错误: {str(e)}")
        return "获取内容失败"

def format_results(results, format_type, top_n, verbose=False):
    """格式化输出：JSON、Markdown 或 HTML"""
    results = results[:top_n]
    
    if format_type == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    elif format_type == "markdown":
        md = "# 搜索结果\n\n"
        for i, result in enumerate(results, 1):
            if verbose:
                print(f"[格式化] 处理Markdown结果 #{i}: {result['title'][:30]}...")
                print(f"[格式化] 获取内容: {result['link']}")
            content = browse_content(result["link"], verbose)
            md += f"## {i}. {result['title']}\n"
            md += f"- **来源**: {result['source']}\n"
            md += f"- **链接**: [{result['link']}]({result['link']})\n"
            md += f"- **摘要**: {result['snippet']}\n"
            md += f"- **内容**: {content}...\n\n"
        if verbose:
            print(f"[格式化] Markdown格式化完成，输出大小: {len(md)}字节")
        return md
    
    elif format_type == "html":
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>搜索结果</title></head>
        <body>
        <h1>搜索结果</h1>
        """
        for i, result in enumerate(results, 1):
            if verbose:
                print(f"[格式化] 处理HTML结果 #{i}: {result['title'][:30]}...")
                print(f"[格式化] 获取内容: {result['link']}")
            content = browse_content(result["link"], verbose)
            html += f"<h2>{i}. {result['title']}</h2>"
            html += f"<p><strong>来源</strong>: {result['source']}</p>"
            html += f"<p><strong>链接</strong>: <a href='{result['link']}'>{result['link']}</a></p>"
            html += f"<p><strong>摘要</strong>: {result['snippet']}</p>"
            html += f"<p><strong>内容</strong>: {content}...</p><hr>"
        html += "</body></html>"
        if verbose:
            print(f"[格式化] HTML格式化完成，输出大小: {len(html)}字节")
        return html

def main():
    parser = argparse.ArgumentParser(description="命令行搜索工具")
    parser.add_argument("--query", required=True, help="搜索查询")
    parser.add_argument("--category", choices=CATEGORY_RESOURCES.keys(), help="强制指定搜索类别")
    parser.add_argument("--include-general", action="store_true", help="在类别搜索外附加通用搜索")
    parser.add_argument("--engine", choices=["duckduckgo", "google"], default="google",
                        help="通用搜索引擎（默认：duckduckgo）")
    parser.add_argument("--top-n", type=int, default=5, help="返回结果数量")
    parser.add_argument("--format", choices=["json", "markdown", "html"], default="json", help="输出格式")
    parser.add_argument("--site", help="限制搜索到特定网站")
    parser.add_argument("--filetype", help="限制搜索到特定文件类型")
    parser.add_argument("--inurl", help="限制搜索到URL包含关键词")
    parser.add_argument("--intitle", help="限制搜索到标题包含关键词")
    parser.add_argument("--intext", help="限制搜索到正文包含关键词")
    parser.add_argument("--allinurl", help="限制搜索到URL包含所有关键词")
    parser.add_argument("--allintitle", help="限制搜索到标题包含所有关键词")
    parser.add_argument("--allintext", help="限制搜索到正文包含所有关键词")
    parser.add_argument("--before", help="限制搜索到指定日期之前（YYYY-MM-DD）")
    parser.add_argument("--after", help="限制搜索到指定日期之后（YYYY-MM-DD）")
    parser.add_argument("--verbose", action="store_true", help="启用详细调试信息输出")
    
    args = parser.parse_args()
    
    # 获取verbose参数
    verbose = args.verbose
    if verbose:
        print("\n[主程序] 启用详细调试模式")
        print(f"[主程序] 搜索查询: {args.query}")
        print(f"[主程序] 命令行参数: {vars(args)}")
    
    # 分类搜索
    if verbose:
        print("\n[主程序] 开始分类搜索...")
        print(f"[主程序] 分析查询类别...")
    category = args.category or classify_query(args.query)
    print(f"搜索类别: {category}")
    if verbose:
        print(f"[主程序] 确定搜索类别: {category}")
    category_results = search_category(category, args.query, args.top_n, args.engine, verbose=verbose)
    
    # 通用搜索（如果指定 --include-general 或 category=general）
    general_results = []
    if args.include_general or category == "general":
        print("执行通用搜索...")
        if verbose:
            print(f"[主程序] 执行通用搜索...")
        general_results = search_engine(args.query, args.engine, max_results=args.top_n, verbose=verbose)
    
    # 限定词搜索（如果提供了任何限定词）
    qualifier_results = []
    if any([args.site, args.filetype, args.inurl, args.intitle, args.intext,
            args.allinurl, args.allintitle, args.allintext, args.before, args.after]):
        print("执行限定词搜索...")
        if verbose:
            print(f"[主程序] 执行限定词搜索...")
        qualifier_results = search_engine(
            args.query, args.engine, args.site, args.filetype, args.inurl, args.intitle, args.intext,
            args.allinurl, args.allintitle, args.allintext, args.before, args.after, args.top_n, verbose=verbose
        )
    
    # 合并结果
    if verbose:
        print(f"\n[主程序] 合并搜索结果...")
        print(f"[主程序] 分类搜索结果: {len(category_results)}条")
        print(f"[主程序] 通用搜索结果: {len(general_results)}条")
        print(f"[主程序] 限定词搜索结果: {len(qualifier_results)}条")
    results = category_results + general_results + qualifier_results
    if verbose:
        print(f"[主程序] 合并后总结果: {len(results)}条")
        print(f"[主程序] 按摘要长度排序结果...")
    results = sorted(results, key=lambda x: len(x["snippet"]), reverse=True)[:args.top_n]
    
    # 格式化输出
    if verbose:
        print(f"\n[主程序] 开始格式化输出，格式: {args.format}")
    output = format_results(results, args.format, args.top_n, verbose=verbose)
    
    # 保存到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.{args.format}"
    if verbose:
        print(f"[主程序] 保存结果到文件: {filename}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"结果已保存至 {filename}")
    if verbose:
        print(f"[主程序] 搜索任务完成")

if __name__ == "__main__":
    main()