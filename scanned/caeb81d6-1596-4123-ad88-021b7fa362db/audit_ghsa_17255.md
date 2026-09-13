# [H] Croogo CMS has a path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-g5p6-3j82-xfm4
CVE: CVE-2024-42718
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-g5p6-3j82-xfm4
Type: github-advisory

## Affected
- Packagist: `croogo/croogo` — affected >=0

## Details
A path traversal vulnerability in Croogo CMS 4.0.7 allows remote attackers to read arbitrary files via a specially crafted path in the 'edit-file' parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42718
- https://github.com/croogo/croogo
- https://github.com/jacopo1223/jacopo.github/tree/main/CVE-2024-42718
