# [M] ProcessWire CMS vulnerable to resource-exhaustion Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-9p44-q66p-xm6p
CVE: CVE-2025-60790
CWE: CWE-400, CWE-409
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-9p44-q66p-xm6p
Type: github-advisory

## Affected
- Packagist: `processwire/processwire` — affected >=0

## Details
ProcessWire CMS 3.0.246 allows a low-privileged user with lang-edit to upload a crafted ZIP to Language Support that is auto-extracted without limits prior to validation, enabling resource-exhaustion Denial of Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60790
- https://github.com/processwire/processwire-issues/issues/2120
- https://github.com/NomanProdhan/security-vulnerability-research/tree/master/CVE-2025-60790
- https://github.com/processwire/processwire
