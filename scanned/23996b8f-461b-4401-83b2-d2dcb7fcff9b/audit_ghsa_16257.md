# [M] Enhavo Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-38m8-5gfc-663g
CVE: CVE-2024-25874
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-38m8-5gfc-663g
Type: github-advisory

## Affected
- Packagist: `enhavo/enhavo-app` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in the New/Edit Article module of Enhavo CMS v0.13.1 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the Create Tag text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25874
- https://github.com/dd3x3r/enhavo/blob/main/xss-create-tag-v0.13.1.md
- https://github.com/enhavo/enhavo-app
- https://www.enhavo.com
