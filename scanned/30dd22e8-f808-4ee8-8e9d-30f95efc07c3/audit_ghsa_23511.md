# [M] Croogo vulnerable to XSS in title field

## Summary
Severity: Medium
Advisory: GHSA-v6q8-8wgx-8hm7
CVE: CVE-2019-7171
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v6q8-8wgx-8hm7
Type: github-advisory

## Affected
- Packagist: `croogo/croogo` — affected >=0 <3.0.7

## Details
A stored-self XSS exists in Croogo through v3.0.5, allowing an attacker to execute HTML or JavaScript code in a vulnerable Title field to /admin/blocks/blocks/edit/8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7171
- https://github.com/croogo/croogo/issues/887
- https://github.com/croogo/croogo/commit/cafaaabe2cef3d1d83652370e30563e6ad7c4158
- https://github.com/croogo/croogo
