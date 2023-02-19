# SEO Scraping

This is a Python script that scrapes a website for metadata and generates an XML file with the collected data. The script uses the requests and beautifulsoup4 libraries to retrieve and parse the HTML of the website, and the xml.etree.ElementTree and xml.dom.minidom libraries to create the XML file.
## Prerequisites

- Python 3.x
- requests library
- beautifulsoup4 library


## Installation

Install this tool with pip

```bash
pip install requests
pip install beautifulsoup4
```
    
## Usage


Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  npm install
```

Start the server

```bash
  npm run start
```


To use the script, open `scrape.py` and update the following line of code:

```python
url = "https://google.com/"
```

Replace `https://google.com/` with the URL of the website you want to scrape.

The script will output an XML file in the same directory as the script, with the name `<title>.xml`. The file will contain the following metadata:

- Title
- Description
- Keywords
- Canonical URL
- Robots
- Open Graph title
- Open Graph description
- Open Graph image
- H1 tags
- H2 tags
- Image alt text

If any of the metadata is missing on the website, the script will insert "missing" as the value for that metadata.