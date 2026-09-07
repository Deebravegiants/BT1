# [M] lxml-html-clean has <base> tag injection through default Cleaner configuration

## Summary
Severity: Medium
Advisory: GHSA-xvp8-3mhv-424c
CVE: CVE-2026-28350
CWE: CWE-116
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-xvp8-3mhv-424c
Type: github-advisory

## Affected
- PyPI: `lxml-html-clean` — affected >=0 <0.4.4

## Details
### Summary
The `<base>` tag passes through the default `Cleaner` configuration. While `page_structure=True` removes `html`, `head`, and `title` tags, there is no specific handling for `<base>`, allowing an attacker to inject it and hijack relative links on the page.

### Details
The `<base>` tag is not currently in the `page_structure` kill set. Even though the specification says `<base>` must be inside `<head>`, browsers accept `<base>` tags outside of the head.

If an attacker injects a `<base>` tag, it changes the base URL for all relative URLs on the page (links, images, scripts) to a domain controlled by the attacker.

### PoC
```python
from lxml_html_clean import clean_html

# The base tag is preserved in the output
result = clean_html('<base href="http://evil.com/"><a href="/account">Account</a>')
print(result)
# Output: <div><base href="http://evil.com/">...<a href="/account">Account</a></div>
```

### Impact
The injection of a `<base>` tag allows an attacker to hijack the resolution of **all** relative URLs on the page. This results in three critical attack vectors:

1.  **Phishing & Redirection:** Attackers can redirect user navigation (e.g., `<a href="/login">`) and form submissions (e.g., `<form action="/auth">`) to an attacker-controlled domain, effectively stealing credentials or sensitive data without the user realizing they have left the legitimate site.
2.  **Cross-Site Scripting (XSS):** If the victim application loads JavaScript files using relative paths (e.g., `<script src="assets/app.js">`), the browser will attempt to fetch the script from the attacker's domain. This upgrades the vulnerability from HTML injection to full Stored XSS.
3.  **Defacement:** Relative references to images (`<img>`) and stylesheets (`<link>`) will be loaded from the attacker's server, allowing for UI redressing or defacement.

## References
- https://github.com/fedora-python/lxml_html_clean/security/advisories/GHSA-xvp8-3mhv-424c
- https://nvd.nist.gov/vuln/detail/CVE-2026-28350
- https://github.com/fedora-python/lxml_html_clean/commit/9c5612ca33b941eec4178abf8a5294b103403f34
- https://github.com/fedora-python/lxml_html_clean
