# [C] xopen is vulnerable to OS Command Injection in Exported Function xopen(filepath)

## Summary
Severity: Critical
Advisory: GHSA-74wf-cwjg-9cf2
CVE: CVE-2020-28447
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-74wf-cwjg-9cf2
Type: github-advisory

## Affected
- npm: `xopen` — affected >=0

## Details
A command injection vulnerability affects all versions of package xopen. The injection point is located in line 14 in index.js in the exported function `xopen(filepath)`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28447
- https://github.com/andrewimm/xopen
- https://github.com/andrewimm/xopen/blob/master/index.js
- https://security.snyk.io/vuln/SNYK-JS-XOPEN-1050981
