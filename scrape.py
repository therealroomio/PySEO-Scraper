import argparse
import json
import os
import re
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import json
import extruct
from w3lib.html import get_base_url
import schema_validator

url = "https://github.com/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

title_tag = soup.find("title")
title = title_tag.text.strip() if title_tag and title_tag.text.strip() else "missing"

metadata = [
    ("description", "meta", {"name": "description"}, "content"),
    ("keywords", "meta", {"name": "keywords"}, "content"),
    ("canonical_url", "link", {"rel": "canonical"}, "href"),
    ("robots", "meta", {"name": "robots"}, "content"),
    ("og_title", "meta", {"property": "og:title"}, "content"),
    ("og_description", "meta", {"property": "og:description"}, "content"),
    ("og_image", "meta", {"property": "og:image"}, "content"),
    ("twitter_title", "meta", {"name": "twitter:title"}, "content"),
    ("twitter_description", "meta", {"name": "twitter:description"}, "content"),
    ("twitter_image", "meta", {"name": "twitter:image"}, "content"),
METADATA_TAGS = [
    ("description", "content"),
    ("keywords", "content"),
    ("canonical_url", "href"),
    ("robots", "content"),
    ("og_title", "content"),
    ("og_description", "content"),
    ("og_image", "content"),
]

def scrape_url(url: str) -> dict:
    """Fetch and parse metadata from the given URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    data = {}
    title_tag = soup.find("title")
    data["title"] = title_tag.text.strip() if title_tag else ""

    for tag, attr in METADATA_TAGS:
        element = soup.find("meta", attrs={"name": tag})
        data[tag] = element.get(attr, "") if element else "missing"

    data["H1"] = [h1.text.strip() for h1 in soup.find_all("h1")]
    data["H2"] = [h2.text.strip() for h2 in soup.find_all("h2")]
    data["Images"] = [img.get("alt", "") for img in soup.find_all("img")]
    return data

def data_to_xml(data: dict) -> str:
    """Convert scraped data to a pretty XML string."""
    root = ET.Element("metadata")
    ET.SubElement(root, "title").text = data.get("title", "")

    for tag, _ in METADATA_TAGS:
        ET.SubElement(root, tag).text = data.get(tag, "")

    h1_parent = ET.SubElement(root, "H1")
    for h1 in data.get("H1", []):
        ET.SubElement(h1_parent, "H1Tag").text = h1

    h2_parent = ET.SubElement(root, "H2")
    for h2 in data.get("H2", []):
        ET.SubElement(h2_parent, "H2Tag").text = h2

    img_parent = ET.SubElement(root, "Images")
    for alt in data.get("Images", []):
        ET.SubElement(img_parent, "ImageAlt").text = alt

    xml_str = ET.tostring(root, encoding="utf-8")
    dom = md.parseString(xml_str)
    return dom.toprettyxml()

def save_output(data: dict, url: str, output_format: str) -> None:
    """Save scraped data for a URL to the desired format in output/ directory."""
    os.makedirs("output", exist_ok=True)
    sanitized = re.sub(r"[^a-zA-Z0-9]+", "_", url)
    filepath = os.path.join("output", f"{sanitized}.{output_format}")

for tag, element_name, attrs, attr in metadata:
    element = soup.find(element_name, attrs=attrs)
    value = (
        element.get(attr).strip()
        if element and element.get(attr) and element.get(attr).strip()
        else "missing"
    )
    ET.SubElement(root, tag).text = value

h1_parent = ET.SubElement(root, "H1")
h1_tags = soup.find_all("h1")
if h1_tags:
    for h1 in h1_tags:
        text = h1.get_text(strip=True)
        ET.SubElement(h1_parent, "H1Tag").text = text if text else "missing"
else:
    ET.SubElement(h1_parent, "H1Tag").text = "missing"

h2_parent = ET.SubElement(root, "H2")
h2_tags = soup.find_all("h2")
if h2_tags:
    for h2 in h2_tags:
        text = h2.get_text(strip=True)
        ET.SubElement(h2_parent, "H2Tag").text = text if text else "missing"
else:
    ET.SubElement(h2_parent, "H2Tag").text = "missing"

img_parent = ET.SubElement(root, "Images")
img_tags = soup.find_all("img")
if img_tags:
    for img in img_tags:
        alt = img.get("alt")
        alt_text = alt.strip() if alt and alt.strip() else "missing"
        ET.SubElement(img_parent, "ImageAlt").text = alt_text
else:
    ET.SubElement(img_parent, "ImageAlt").text = "missing"

structured_results = []

# JSON-LD scripts
for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.string)
    except (json.JSONDecodeError, TypeError):
        continue
    items = data if isinstance(data, list) else [data]
    for item in items:
        errors = schema_validator.validate(item)
        structured_results.append(("json-ld", item.get("@type"), errors))

# Microdata
base_url = get_base_url(response.text, url)
extracted = extruct.extract(response.text, base_url=base_url, syntaxes=["microdata"])
for item in extracted.get("microdata", []):
    schema_type_url = item.get("type")
    schema_type = schema_type_url.split("/")[-1] if schema_type_url else None
    data = {"@type": schema_type}
    properties = item.get("properties", {})
    if isinstance(properties, dict):
        data.update(properties)
    errors = schema_validator.validate(data)
    structured_results.append(("microdata", schema_type, errors))

sd_parent = ET.SubElement(root, "StructuredData")
for source, sd_type, errors in structured_results:
    item_elem = ET.SubElement(sd_parent, "Item")
    ET.SubElement(item_elem, "Source").text = source
    ET.SubElement(item_elem, "Type").text = sd_type or ""
    if errors:
        ET.SubElement(item_elem, "Valid").text = "false"
        errors_elem = ET.SubElement(item_elem, "Errors")
        for err in errors:
            ET.SubElement(errors_elem, "Error").text = err
    else:
        ET.SubElement(item_elem, "Valid").text = "true"

tree = ET.ElementTree(root)
filename = " ".join(title.split()[:2]) + ".xml" if title != "missing" else "output.xml"
    if output_format == "xml":
        content = data_to_xml(data)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    print(f"Output written to: {filepath}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape metadata from URLs")
    parser.add_argument("--url", action="append", help="URL to scrape")
    parser.add_argument("--file", help="File containing URLs (one per line)")
    parser.add_argument("--output-format", choices=["xml", "json"], default="xml")

    args = parser.parse_args()

    urls = []
    if args.url:
        urls.extend(args.url)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            urls.extend(line.strip() for line in f if line.strip())

    if not urls:
        parser.error("No URLs provided. Use --url or --file.")

    for url in urls:
        data = scrape_url(url)
        save_output(data, url, args.output_format)

for source, sd_type, errors in structured_results:
    if errors:
        print(f"{source} {sd_type} validation errors:")
        for err in errors:
            print(f" - {err}")
    else:
        print(f"{source} {sd_type} is valid")

if not structured_results:
    print("No structured data found")

print("Output written to:", filename)

if __name__ == "__main__":
    main()
