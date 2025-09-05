import re
from collections import Counter
from typing import List, Dict, Any


def analyze(soup) -> Dict[str, Any]:
    """Analyze a BeautifulSoup object for basic SEO metrics.

    Returns a dictionary with title and meta description lengths,
    heading hierarchy, keyword density and any generated warnings.
    """
    warnings: List[str] = []

    # Title length
    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    title_length = len(title_text)
    if title_length == 0 or title_length > 60:
        warnings.append(f"Title length {title_length} characters.")

    # Meta description length
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc_text = desc_tag.get("content", "").strip() if desc_tag else ""
    meta_length = len(desc_text)
    if meta_length == 0 or not 50 <= meta_length <= 160:
        warnings.append(f"Meta description length {meta_length} characters.")

    # Heading hierarchy
    heading_tags = soup.find_all(re.compile("^h[1-6]$"))
    hierarchy = [int(tag.name[1]) for tag in heading_tags]
    for i in range(1, len(hierarchy)):
        if hierarchy[i] > hierarchy[i - 1] + 1:
            warnings.append("Improper heading hierarchy.")
            break

    # Keyword density
    body_text = soup.get_text(" ", strip=True)
    words = re.findall(r"\b\w+\b", body_text.lower())
    total_words = len(words) or 1
    counts = Counter(words)
    density = [
        {
            "keyword": word,
            "count": count,
            "density": round(count / total_words * 100, 2),
        }
        for word, count in counts.most_common(10)
    ]

    summary = _summary_table(title_length, meta_length, hierarchy, density)
    return {
        "title_length": title_length,
        "meta_description_length": meta_length,
        "heading_hierarchy": hierarchy,
        "keyword_density": density,
        "warnings": warnings,
        "summary": summary,
    }


def _summary_table(title_len: int, meta_len: int, hierarchy: List[int], density: List[Dict[str, Any]]) -> str:
    """Create a simple text table summarizing the analysis."""
    rows = [
        ("Title Length", str(title_len)),
        ("Meta Description Length", str(meta_len)),
        (
            "Heading Hierarchy",
            " > ".join(f"H{lvl}" for lvl in hierarchy) if hierarchy else "",
        ),
    ]
    top_keywords = ", ".join(
        f"{item['keyword']} ({item['density']}%)" for item in density[:3]
    )
    rows.append(("Top Keywords", top_keywords))

    col_width = max(len(r[0]) for r in rows) + 2
    lines = [f"{'Metric'.ljust(col_width)}Value", f"{'-' * (col_width + 5)}"]
    for metric, value in rows:
        lines.append(f"{metric.ljust(col_width)}{value}")
    return "\n".join(lines)
