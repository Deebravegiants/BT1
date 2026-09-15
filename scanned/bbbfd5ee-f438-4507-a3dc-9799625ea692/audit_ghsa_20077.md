# [C] cycle-import-check vulnerable to Command Injection

## Summary
Severity: Critical
Advisory: GHSA-995x-33wq-8gc9
CVE: CVE-2022-24377
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-995x-33wq-8gc9
Type: github-advisory

## Affected
- npm: `cycle-import-check` — affected >=0 <1.3.2

## Details
The package cycle-import-check before version 1.3.2 is vulnerable to Command Injection via the `writeFileToTmpDirAndOpenIt` function due to improper user-input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24377
- https://github.com/Soontao/cycle-import-check/commit/1ca97b59df7e9c704471fcb4cf042ce76d7c9890
- https://github.com/Soontao/cycle-import-check
- https://security.snyk.io/vuln/SNYK-JS-CYCLEIMPORTCHECK-3157955
