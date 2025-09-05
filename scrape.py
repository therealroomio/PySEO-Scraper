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

title = soup.find("title").text.strip()

metadata = [
    ("description", "content"),
    ("keywords", "content"),
    ("canonical_url", "href"),
    ("robots", "content"),
    ("og_title", "content"),
    ("og_description", "content"),
    ("og_image", "content")
]

root = ET.Element("metadata")
ET.SubElement(root, "title").text = title

for tag, attr in metadata:
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
filename = " ".join(title.split()[:2]) + ".xml"

xml_str = ET.tostring(root, encoding="utf-8")
dom = md.parseString(xml_str)

with open(filename, "w") as f:
    f.write(dom.toprettyxml())

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

