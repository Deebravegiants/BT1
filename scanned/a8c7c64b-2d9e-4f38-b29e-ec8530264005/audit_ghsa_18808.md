# [M] QGIS QWC2 Cross-Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gxp8-m5rq-3m38
CVE: CVE-2025-11183
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/AU:N/RE:L (CVSS_V4)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-gxp8-m5rq-3m38
Type: github-advisory

## Affected
- npm: `qwc2` — affected >=0 <2025.08.14

## Details
Cross-Site Scripting vulnerability in attribute table in QGIS QWC2 < 2025.08.14 allows an authorized attacker to plant arbitrary JavaScript code in the page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11183
- https://github.com/qgis/qwc2
- https://hub.ntc.swiss/ntcf-2025-4286
