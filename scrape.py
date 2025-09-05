import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

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
]

root = ET.Element("metadata")
ET.SubElement(root, "title").text = title

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

tree = ET.ElementTree(root)
filename = " ".join(title.split()[:2]) + ".xml" if title != "missing" else "output.xml"

xml_str = ET.tostring(root, encoding="utf-8")
dom = md.parseString(xml_str)

with open(filename, "w") as f:
    f.write(dom.toprettyxml())

print("Output written to:", filename)