# [M] Denial of Service in SheetsJS Pro

## Summary
Severity: Medium
Advisory: GHSA-8vcr-vxm8-293m
CVE: CVE-2021-32013
CWE: CWE-400
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-22
Source: https://github.com/advisories/GHSA-8vcr-vxm8-293m
Type: github-advisory

## Affected
- npm: `xlsx` — affected >=0 <0.17.0
- Maven: `org.webjars.npm:xlsx` — affected >=0 <0.17.0

## Details
SheetJS Pro through 0.16.9 allows attackers to cause a denial of service (memory consumption) via a crafted .xlsx document that is mishandled when read by xlsx.js (issue 2 of 2).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32013
- https://floqast.com/engineering-blog/post/fuzzing-and-parsing-securely
- https://sheetjs.com/pro
- https://www.npmjs.com/package/xlsx/v/0.17.0
- https://www.oracle.com/security-alerts/cpujan2022.html
