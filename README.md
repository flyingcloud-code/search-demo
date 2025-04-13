# Search Demo
A comprehensive multi-source search tool that intelligently categorizes queries and searches across specialized sources to provide relevant results.

## Problem Statement
Traditional search engines often provide general results but lack specialized knowledge from academic, technical, or domain-specific sources. Users frequently need to manually search multiple platforms to gather comprehensive information on a topic.

## Purpose
Search Demo solves this problem by:

- Automatically classifying search queries by type (academic, knowledge, product, policy, or general)
- Searching appropriate specialized sources based on the query category
- Consolidating results from multiple sources into a single output
- Supporting advanced search qualifiers for precise searches
- Providing results in multiple formats (JSON, Markdown, HTML)
## Architecture
The application follows a modular architecture:

1. Query Classification : Analyzes the query to determine its category
   
   - Academic: Research papers, academic studies
   - Knowledge: Definitions, historical information
   - Product: Reviews, recommendations
   - Policy: News, regulations
   - General: Default category for other queries
2. Specialized Search Modules :
   
   - Academic: arXiv and Google Scholar
   - Knowledge: Wikipedia
   - Product: TechRadar, CNET, and Reddit
   - Policy: USTR and Reuters
   - General: DuckDuckGo and Google
3. Result Processing : Consolidates, filters, and ranks results
4. Output Formatting : Converts results to JSON, Markdown, or HTML
## Installation
### Prerequisites
- Python 3.6+
- pip (Python package manager)
### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/search-demo.git
cd search-demo
 ```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Required Packages
Create a requirements.txt file with the following content:

```bash
arxiv
wikipedia
duckduckgo_search
googlesearch-python
scholarly
requests
beautifulsoup4
```

Then install with:

```bash
pip install -r requirements.txt
```

## Usage
### Basic Usage
```bash
python search.py --query "artificial intelligence ethics" --format markdown
```


### Command Line Parameters Parameter Description Default --query

Search query (required)

- --category

Force specific search category (academic, knowledge, product, policy, general)

Auto-detected --include-general

Include general search results in addition to category-specific results

False --engine

General search engine to use (duckduckgo, google)

duckduckgo --top-n

Number of results to return

--format

Output format (json, markdown, html)

--verbose

Enable detailed debug output

False
### Search Qualifiers
The tool supports various search qualifiers to refine results:
 Qualifier Description Example --site

Limit search to specific website

--site "example.com" --filetype

Limit search to specific file type

--filetype "pdf" --inurl

Limit search to URLs containing keyword

--inurl "blog" --intitle

Limit search to titles containing keyword

--intitle "guide" --intext

Limit search to content containing keyword

--intext "tutorial" --before

Limit search to before date (YYYY-MM-DD)

--before "2023-01-01" --after

Limit search to after date (YYYY-MM-DD)

--after "2022-01-01"
## Examples
### Academic Search
```bash
# Search for academic papers on transformer models
python search.py --query "transformer neural networks" --category academic --format markdown

# Search for recent AI ethics papers with date filter
python search.py --query "AI ethics" --category academic --after "2023-01-01" --format json

# Search arXiv for machine learning papers with verbose output
python search.py --query "machine learning" --category academic --engine arxiv --verbose
```

### Product Search
```bash
# Search for product reviews on gaming laptops
python search.py --query "best gaming laptops 2023" --category product --format html

# Search Reddit for smartphone recommendations
python search.py --query "best smartphone 2023" --category product --site "reddit.com" --format markdown

# Search multiple tech sites for laptop reviews
python search.py --query "Dell XPS 15 review" --category product --include-general --top-n 10
```

### Knowledge Search
```bash
# Get Wikipedia summary of quantum computing
python search.py --query "quantum computing" --category knowledge --verbose

# Search for historical events with date range
python search.py --query "world war 2 events" --category knowledge --before "1945-12-31" --after "1939-01-01"
```

### Policy Search
```bash
# Search for trade policy news
python search.py --query "US China trade policy" --category policy --format html

# Search Reuters for economic news
python search.py --query "economic forecast 2023" --category policy --site "reuters.com"
```

### General Search with Qualifiers
```bash
# Search for PDF tutorials on Python
python search.py --query "Python tutorial" --filetype "pdf" --format json

# Search specific site for documentation
python search.py --query "Django REST framework" --site "django-rest-framework.org"

# Search with multiple qualifiers
python search.py --query "data science" --intitle "guide" --inurl "blog" --after "2022-01-01"
```


## Output
Results are saved to a file named search_results_YYYYMMDD_HHMMSS.{format} in the current directory, where format is json, markdown, or html based on your selection.

## Advanced Features
- Intelligent Query Classification : Automatically determines the best sources to search based on query content
- Multi-Source Integration : Combines results from specialized and general search engines
- Content Extraction : Retrieves and summarizes content from result pages
- Flexible Output Formats : Supports JSON (for programmatic use), Markdown (for documentation), and HTML (for web display)
## Limitations
- Some search sources may have rate limits or require API keys for extended use
- Content extraction may be limited for sites with complex JavaScript rendering
- Google Scholar searches may occasionally be blocked due to anti-scraping measures