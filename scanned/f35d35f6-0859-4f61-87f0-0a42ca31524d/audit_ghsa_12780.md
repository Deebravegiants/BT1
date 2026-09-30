# [C] Command injection in vagrant.js

## Summary
Severity: Critical
Advisory: GHSA-54jw-jqr9-6cj9
CVE: CVE-2022-25962
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-54jw-jqr9-6cj9
Type: github-advisory

## Affected
- npm: `vagrant.js` — affected >=0

## Details
All versions of the package vagrant.js are vulnerable to Command Injection via the boxAdd function due to improper input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25962
- https://github.com/cakecatz/vagrant.js
- https://security.snyk.io/vuln/SNYK-JS-VAGRANTJS-3175614
