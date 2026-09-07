# [M] Cross-site Scripting in yapi-vendor

## Summary
Severity: Medium
Advisory: GHSA-4jqw-vfmj-9rmh
CVE: CVE-2021-36686
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-4jqw-vfmj-9rmh
Type: github-advisory

## Affected
- npm: `yapi-vendor` — affected >=0

## Details
Cross Site Scripting (XSS) vulnerability in yapi 1.9.1 allows attackers to execute arbitrary code via the /interface/api edit page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36686
- https://github.com/YMFE/yapi/issues/2190
- https://github.com/YMFE/yapi/issues/2240
- https://github.com/YMFE/yapi
