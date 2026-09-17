# [M] Electron vulnerable to URL spoofing via PDFium

## Summary
Severity: Medium
Advisory: GHSA-6h98-cf9g-vmg2
CVE: CVE-2017-1000424
CWE: CWE-290, CWE-345
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6h98-cf9g-vmg2
Type: github-advisory

## Affected
- npm: `electron` — affected >=1.7.0 <1.7.6

## Details
Electron version 1.7.0 - 1.7.5 is vulnerable to a URL Spoofing problem when opening PDFs in PDFium resulting loading arbitrary PDFs that a hacker can control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000424
- https://github.com/electron/electron/pull/10008
- https://github.com/electron/electron/pull/10008/files
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v1.7.6
