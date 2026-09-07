# [M] Gleez Cms Cross-site Scripting in Profile Page

## Summary
Severity: Medium
Advisory: GHSA-q9g7-pff4-548r
CVE: CVE-2018-1999021
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q9g7-pff4-548r
Type: github-advisory

## Affected
- Packagist: `gleez/cms` — affected >=0

## Details
Gleezcms Gleez Cms version 1.3.0 contains a Cross Site Scripting (XSS) vulnerability in Profile page that can result in injection of arbitrary web script or HTML via the profile page editor. The victim must navigate to the attacker's profile page to exploit this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999021
- https://github.com/gleez/cms/issues/797
- https://github.com/gleez/cms
