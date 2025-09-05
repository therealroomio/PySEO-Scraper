import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def fetch_text(url: str) -> str:
    """Return text content of URL or an error message."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        return f"HTTP {response.status_code}"
    except requests.RequestException as exc:
        return f"Error: {exc}"


def audit_page(url: str, skip_links: bool = False):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    broken_links = []
    if not skip_links:
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            href = urljoin(url, href)
            try:
                link_resp = requests.head(href, allow_redirects=True, timeout=10)
                if link_resp.status_code >= 400:
                    broken_links.append(f"{href} (HTTP {link_resp.status_code})")
            except requests.RequestException as exc:
                broken_links.append(f"{href} (Error: {exc})")

    missing_alts = []
    for img in soup.find_all("img"):
        if not img.get("alt"):
            missing_alts.append(img.get("src", ""))

    parsed = urlparse(url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    robots_txt = fetch_text(urljoin(root, "robots.txt"))
    sitemap_xml = fetch_text(urljoin(root, "sitemap.xml"))

    return {
        "broken_links": broken_links,
        "missing_alts": missing_alts,
        "robots_txt": robots_txt,
        "sitemap_xml": sitemap_xml,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit links and image alts on a web page")
    parser.add_argument("url", help="URL of page to audit")
    parser.add_argument("--skip-links", action="store_true", dest="skip_links", help="Skip checking <a> targets")
    args = parser.parse_args()

    report = audit_page(args.url, skip_links=args.skip_links)

    print("Robots.txt snippet:\n", report["robots_txt"][:200])
    print("\nSitemap.xml snippet:\n", report["sitemap_xml"][:200])

    print("\nBroken links:")
    if report["broken_links"]:
        for link in report["broken_links"]:
            print(" -", link)
    else:
        print(" None")

    print("\nImages missing alt text:")
    if report["missing_alts"]:
        for img_src in report["missing_alts"]:
            print(" -", img_src)
    else:
        print(" None")


if __name__ == "__main__":
    main()
