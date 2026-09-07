# [H] Cross Site Request Forgery in intelliants/subrion

## Summary
Severity: High
Advisory: GHSA-9cc3-5w85-pxvx
CVE: CVE-2020-18326
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-05
Source: https://github.com/advisories/GHSA-9cc3-5w85-pxvx
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
Cross Site Request Forgery (CSRF) vulnerability exists in Intelliants Subrion CMS v4.2.1 via the Members administrator function, which could let a remote unauthenticated malicious user send an authorised request to victim and successfully create an arbitrary administrator user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-18326
- https://github.com/hamm0nz/CVE-2020-18326
- https://github.com/intelliants/subrion
