# [H] Connect-Multiparty allows arbitrary file upload

## Summary
Severity: High
Advisory: GHSA-w2xw-44r3-4v9g
CVE: CVE-2022-29623
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w2xw-44r3-4v9g
Type: github-advisory

## Affected
- npm: `connect-multiparty` — affected >=0

## Details
An arbitrary file upload vulnerability in the file upload module of Express Connect-Multiparty 2.2.0 allows attackers to execute arbitrary code via a crafted PDF file. NOTE: the Supplier has not verified this vulnerability report.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29623
- https://github.com/expressjs/connect-multiparty
- https://github.com/expressjs/connect-multiparty/releases/tag/2.2.0
- https://www.npmjs.com/package/connect-multiparty
- https://www.youtube.com/watch?v=i3xJR-91rrM
