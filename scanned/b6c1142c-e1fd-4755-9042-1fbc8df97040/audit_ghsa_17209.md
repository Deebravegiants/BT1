# [M] Django MarkdownX Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fvx8-79hx-x82f
CVE: CVE-2024-2319
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-08
Source: https://github.com/advisories/GHSA-fvx8-79hx-x82f
Type: github-advisory

## Affected
- PyPI: `django-markdownx` — affected >=0

## Details
Cross-Site Scripting (XSS) vulnerability in the Django MarkdownX project, affecting version 4.0.2. An attacker could store a specially crafted JavaScript payload in the upload functionality due to lack of proper sanitisation of JavaScript elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2319
- https://github.com/neutronX/django-markdownx
- https://www.incibe.es/en/incibe-cert/notices/aviso/cross-site-scripting-vulnerability-django-markdownx
