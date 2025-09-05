# SEO Scraping

This is a Python script that scrapes a website for metadata and generates an XML file with the collected data. The script uses the requests and beautifulsoup4 libraries to retrieve and parse the HTML of the website, and the xml.etree.ElementTree and xml.dom.minidom libraries to create the XML file.

![SEO Scraping](./screenshot.png)

## Prerequisites

- Python 3.x
- requests library
- beautifulsoup4 library


## Installation

Install this tool with pip

```
pip install requests
pip install beautifulsoup4
```
    
## Usage


Clone the project

```
  git clone https://github.com/therealroomio/PySEO-Scraper
```

Go to the project directory

```
  cd PySEO-Scraper
```

Install dependencies

```
  pip install requests
  pip install beautifulsoup4
```

To use the script, open `scrape.py` and update the following line of code:

```python
url = "https://google.com/"
```

Replace `https://google.com/` with the URL of the website you want to scrape then run it in Python.

```python
python3 scrape.py
```

The script will output an XML file in the same directory as the script, with the name `<title>.xml`. The file will contain the following metadata:

- Title
- Description
- Keywords
- Canonical URL (from `<link rel="canonical">`)
- Robots
- Open Graph title
- Open Graph description
- Open Graph image
- Twitter title
- Twitter description
- Twitter image
- H1 tags
- H2 tags
- Image alt text
- SEO audit warnings (title/meta lengths, heading hierarchy, keyword density)

If any of the metadata is missing on the website, the script will insert "missing" as the value for that metadata.

## Link Audit

`link_audit.py` checks a page for broken `<a>` links, images missing alt text, and retrieves `robots.txt` and `sitemap.xml` from the target domain.

```bash
python link_audit.py https://example.com
```

To skip checking link targets use:

```bash
python link_audit.py https://example.com --skip-links
=======
The generated report also contains a short summary table of the key SEO metrics.

## Authors

[@therealroomio](https://www.github.com/therealroomio) using ChatGPT

