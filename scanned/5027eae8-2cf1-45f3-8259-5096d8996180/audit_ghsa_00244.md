# [M] Cross-Site Scripting in connect

## Summary
Severity: Medium
Advisory: GHSA-rch9-xh7r-mqgw
CVE: CVE-2018-3717
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-rch9-xh7r-mqgw
Type: github-advisory

## Affected
- npm: `connect` — affected >=0 <2.14.0

## Details
connect node module before 2.14.0 suffers from a Cross-Site Scripting (XSS) vulnerability due to a lack of validation of file in directory.js middleware.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3717
- https://github.com/JacksonTian/anywhere/issues/33#issuecomment-366527448
- https://github.com/senchalabs/connect/commit/6d5dd30075d2bc4ee97afdbbe3d9d98d8d52d74b
- https://hackerone.com/reports/309394
- https://hackerone.com/reports/309641
- https://github.com/advisories/GHSA-rch9-xh7r-mqgw
- https://www.npmjs.com/advisories/584
- https://www.npmjs.com/advisories/595
