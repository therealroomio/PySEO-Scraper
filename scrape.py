import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

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

tree = ET.ElementTree(root)
filename = " ".join(title.split()[:2]) + ".xml"

xml_str = ET.tostring(root, encoding="utf-8")
dom = md.parseString(xml_str)

with open(filename, "w") as f:
    f.write(dom.toprettyxml())

print("Output written to:", filename)