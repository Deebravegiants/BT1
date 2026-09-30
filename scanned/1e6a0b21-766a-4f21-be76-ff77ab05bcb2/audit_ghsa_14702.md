# [H] TCPDF has incorrect comparison

## Summary
Severity: High
Advisory: GHSA-w95c-7994-ghpr
CVE: CVE-2024-56522
CWE: CWE-697, CWE-843
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-27
Source: https://github.com/advisories/GHSA-w95c-7994-ghpr
Type: github-advisory

## Affected
- Packagist: `tecnickcom/tcpdf` — affected >=0 <6.8.0

## Details
An issue was discovered in TCPDF before 6.8.0. unserializeTCPDFtag uses != (aka loose comparison) and does not use a constant-time function to compare TCPDF tag hashes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56522
- https://github.com/tecnickcom/TCPDF/commit/d54b97cec33f4f1a5ad81119a82085cad93cec89
- https://github.com/tecnickcom/TCPDF
- https://github.com/tecnickcom/TCPDF/compare/6.7.8...6.8.0
- https://lists.debian.org/debian-lts-announce/2025/06/msg00004.html
- https://tcpdf.org
- https://www.php.net/manual/en/types.comparisons.php
