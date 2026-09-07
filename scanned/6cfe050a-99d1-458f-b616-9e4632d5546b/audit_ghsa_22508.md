# [M] Croogo vulnerable to XSS in Blog field

## Summary
Severity: Medium
Advisory: GHSA-9f9r-w3xq-f722
CVE: CVE-2019-7168
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9f9r-w3xq-f722
Type: github-advisory

## Affected
- Packagist: `croogo/croogo` — affected >=0 <3.0.7

## Details
A stored-self XSS exists in Croogo through v3.0.5, allowing an attacker to execute HTML or JavaScript code in a vulnerable Blog field to `/admin/nodes/nodes/add/blog`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7168
- https://github.com/croogo/croogo/issues/886
- https://github.com/croogo/croogo/commit/cafaaabe2cef3d1d83652370e30563e6ad7c4158
- https://github.com/croogo/croogo
