# [C] Command injection in buns

## Summary
Severity: Critical
Advisory: GHSA-487w-pqcm-63hq
CVE: CVE-2020-7794
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-01-13
Source: https://github.com/advisories/GHSA-487w-pqcm-63hq
Type: github-advisory

## Affected
- npm: `buns` — affected >=0

## Details
There is a command injection vulnerability in all versions of package buns. The injection point is located in line 678 in index file lib/index.js in the exported function install(requestedModule).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7794
- https://snyk.io/vuln/SNYK-JS-BUNS-1050389
