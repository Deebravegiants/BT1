# [H] OpenCart Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-jwqr-jcwp-445w
CVE: CVE-2018-13067
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jwqr-jcwp-445w
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=0

## Details
`/upload/catalog/controller/account/password.php` in OpenCart through 3.0.2.0 has CSRF via the `index.php?route=account/password` URI to change a user's password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13067
- https://github.com/opencart/opencart/issues/6912
- https://github.com/opencart/opencart
- https://whitehatck01.blogspot.com/2018/06/opencart-v3-0-3-0-user-changes-password.html
