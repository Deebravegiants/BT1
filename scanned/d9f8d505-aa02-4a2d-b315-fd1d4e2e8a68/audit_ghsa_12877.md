# [C] wifey vulnerable to Command Injection due to improper input sanitization

## Summary
Severity: Critical
Advisory: GHSA-xj9v-6q2f-vqhx
CVE: CVE-2022-25890
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-xj9v-6q2f-vqhx
Type: github-advisory

## Affected
- npm: `wifey` — affected >=0

## Details
All versions of the package wifey are vulnerable to Command Injection via the `connect()` function due to improper input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25890
- https://security.snyk.io/vuln/SNYK-JS-WIFEY-3175615
