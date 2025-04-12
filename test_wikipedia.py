# 测试Wikipedia搜索功能
import sys
sys.path.append('c:\\work\\github\\deepsearch_demo')
from search import search_wikipedia

# 使用verbose模式测试搜索功能
results = search_wikipedia('artificial intelligence', verbose=True)
print("\n搜索结果:")
for i, result in enumerate(results):
    print(f"\n结果 #{i+1}:")
    print(f"标题: {result['title']}")
    print(f"链接: {result['link']}")
    print(f"摘要: {result['snippet']}")