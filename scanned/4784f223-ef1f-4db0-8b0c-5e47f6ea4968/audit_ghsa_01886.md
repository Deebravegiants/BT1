# [C]  OS Command Injection in adb-driver

## Summary
Severity: Critical
Advisory: GHSA-4m6q-rxhm-675w
CVE: CVE-2020-7636
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-4m6q-rxhm-675w
Type: github-advisory

## Affected
- npm: `adb-driver` — affected >=0

## Details
adb-driver through 0.1.8 is vulnerable to Command Injection.It allows execution of arbitrary commands via the command function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7636
- https://snyk.io/vuln/SNYK-JS-ADBDRIVER-564430
- https://www.npmjs.com/package/adb-driver
