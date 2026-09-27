# [M] WeasyPrint has CSS Injection via Presentational Hints

## Summary
Severity: Medium
Advisory: GHSA-jhhc-3hcp-qhm5
CVE: CVE-2026-49452
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-jhhc-3hcp-qhm5
Type: github-advisory

## Affected
- PyPI: `weasyprint` — affected >=0

## Details
### Summary
A CSS injection issue exists in WeasyPrint when HTML presentational hints are enabled. Unescaped attribute values are embedded into CSS, allowing injection of arbitrary CSS declarations. This affects applications processing untrusted HTML input.

### Details
File: weasyprint/css/__init__.py

The `background` attribute is used to construct CSS:

background-image:url({element.get("background")})

This string is parsed by `tinycss2.parse_blocks_contents()`.

Because the value is not escaped, additional CSS declarations can be injected.

### PoC
<body background="x);background-image:url(http://169.254.169.254/latest/meta-data/)">

### Impact
- CSS injection
- Server-side requests via injected `url()`
- Limited to cases where `presentational_hints=True`

### Suggested Fix
- Escape attribute values before embedding into CSS
- Restrict allowed values for presentational hints
[VULN-05_css_injection_presentational_hints.md](https://github.com/user-attachments/files/26370718/VULN-05_css_injection_presentational_hints.md)

## References
- https://github.com/Kozea/WeasyPrint/security/advisories/GHSA-jhhc-3hcp-qhm5
- https://github.com/Kozea/WeasyPrint
