# [M] alextselegidis/easyappointments Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fc4g-f42p-7rhp
CVE: CVE-2023-2104
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-15
Source: https://github.com/advisories/GHSA-fc4g-f42p-7rhp
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected >=0

## Details
alextselegidis/easyappointments 1.4.3 and prior allows one provider to view and edit others providers' appointment details. A patch is available at commit 75b24735767868344193fb2cc56e17ee4b9ac4be and anticipated to be part of version 1.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2104
- https://github.com/alextselegidis/easyappointments/commit/75b24735767868344193fb2cc56e17ee4b9ac4be
- https://github.com/alextselegidis/easyappointments
- https://huntr.dev/bounties/3099b8d1-c49c-41b8-a929-73ccded6fc7c
