# [C] Prototype pollution in dotty

## Summary
Severity: Critical
Advisory: GHSA-f5c9-x9j6-87qp
CVE: CVE-2021-25912
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-02-05
Source: https://github.com/advisories/GHSA-f5c9-x9j6-87qp
Type: github-advisory

## Affected
- npm: `dotty` — affected >=0 <0.1.1

## Details
Prototype pollution vulnerability in 'dotty' before version 0.1.1 allows attackers to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25912
- https://github.com/deoxxa/dotty/commit/cd997d37917186c131be71501a698803f2b7ebdb
- https://www.npmjs.com/package/dotty
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25912
