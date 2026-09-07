# [M] ezplatform-admin-ui Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-99rh-vxmc-7wgf
CVE: CVE-2019-12139
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-99rh-vxmc-7wgf
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-admin-ui` — affected >=1.3 <1.3.5
- Packagist: `ezsystems/ezplatform-admin-ui` — affected >=1.4 <1.4.4

## Details
An XSS issue was discovered in the Admin UI in eZ Platform 2.x. This affects ezplatform-admin-ui 1.3.x before 1.3.5 and 1.4.x before 1.4.4, and ezplatform-page-builder 1.1.x before 1.1.5 and 1.2.x before 1.2.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12139
- https://share.ez.no/community-project/security-advisories/ezsa-2019-001-xss-in-admin-ui
