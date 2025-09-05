import argparse
import json
import os
import re
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

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

if __name__ == "__main__":
    main()
