# [C] Command injection in gitlogplus

## Summary
Severity: Critical
Advisory: GHSA-3fxp-vwxm-2r5p
CVE: CVE-2021-23412
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-3fxp-vwxm-2r5p
Type: github-advisory

## Affected
- npm: `gitlogplus` — affected >=0

## Details
All versions of package gitlogplus are vulnerable to Command Injection via the main functionality, as options attributes are appended to the command to be executed without sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23412
- https://hackerone.com/reports/808942
- https://snyk.io/vuln/SNYK-JS-GITLOGPLUS-1315832
- https://www.npmjs.com/package/gitlogplus
