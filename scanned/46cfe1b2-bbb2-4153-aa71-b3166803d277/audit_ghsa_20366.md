# [H] OS Command Injection in gitsome

## Summary
Severity: High
Advisory: GHSA-9v73-x562-wv5x
CVE: CVE-2021-34081
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-9v73-x562-wv5x
Type: github-advisory

## Affected
- npm: `gitsome` — affected >=0

## Details
OS Command Injection vulnerability in bbultman gitsome through 0.2.3 allows attackers to execute arbitrary commands via a crafted tag name of the target git repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34081
- https://advisory.checkmarx.net/advisory/CX-2021-4780
- https://www.npmjs.com/package/gitsome
