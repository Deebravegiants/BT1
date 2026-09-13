# [H] OS Command Injection in lsof

## Summary
Severity: High
Advisory: GHSA-whq6-mj2r-mjqc
CVE: CVE-2019-10783
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-whq6-mj2r-mjqc
Type: github-advisory

## Affected
- npm: `lsof` — affected >=0

## Details
All versions including 0.0.4 of lsof npm module are vulnerable to Command Injection. Every exported method used by the package uses the exec function to parse user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10783
- https://snyk.io/vuln/SNYK-JS-LSOF-543632
