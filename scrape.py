import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

import seo_audit

METADATA = [
    ("description", "content"),
    ("keywords", "content"),
    ("canonical_url", "href"),
    ("robots", "content"),
    ("og_title", "content"),
    ("og_description", "content"),
    ("og_image", "content"),
]


def scrape(url: str):
    """Scrape the given URL and return metadata with SEO audit warnings."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else ""

    root = ET.Element("metadata")
    ET.SubElement(root, "title").text = title

    for tag, attr in METADATA:
        element = soup.find("meta", attrs={"name": tag})
        if element:
            ET.SubElement(root, tag).text = element.get(attr, "")
        else:
            ET.SubElement(root, tag).text = "missing"

    h1_parent = ET.SubElement(root, "H1")
    for h1 in soup.find_all("h1"):
        ET.SubElement(h1_parent, "H1Tag").text = h1.text.strip()

    h2_parent = ET.SubElement(root, "H2")
    for h2 in soup.find_all("h2"):
        ET.SubElement(h2_parent, "H2Tag").text = h2.text.strip()

    img_parent = ET.SubElement(root, "Images")
    for img in soup.find_all("img"):
        ET.SubElement(img_parent, "ImageAlt").text = img.get("alt", "")

    audit = seo_audit.analyze(soup)
    warnings_parent = ET.SubElement(root, "Warnings")
    for warning in audit["warnings"]:
        ET.SubElement(warnings_parent, "Warning").text = warning

    summary_parent = ET.SubElement(root, "Summary")
    summary_parent.text = "\n" + audit["summary"]

    xml_str = ET.tostring(root, encoding="utf-8")
    dom = md.parseString(xml_str)

    filename = " ".join(title.split()[:2]) + ".xml"
    with open(filename, "w") as f:
        f.write(dom.toprettyxml())

    print("Output written to:", filename)
    return {"warnings": audit["warnings"], "filename": filename}


if __name__ == "__main__":
    URL = "https://github.com/"
    scrape(URL)
