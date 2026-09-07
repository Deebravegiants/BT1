# [C] Improper neutralization of arguments in freediskspace

## Summary
Severity: Critical
Advisory: GHSA-4gfq-6m28-m5mg
CVE: CVE-2020-7775
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-4gfq-6m28-m5mg
Type: github-advisory

## Affected
- npm: `freediskspace` — affected >=0

## Details
This affects all versions of package freediskspace. The vulnerability arises out of improper neutralization of arguments in line 71 of freediskspace.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7775
- https://snyk.io/vuln/SNYK-JS-FREEDISKSPACE-1040716
