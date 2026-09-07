# [H] SQL injection in opencart

## Summary
Severity: High
Advisory: GHSA-7crj-24g3-g7h7
CVE: CVE-2024-21514
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-06-22
Source: https://github.com/advisories/GHSA-7crj-24g3-g7h7
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=0

## Details
This affects versions of the package opencart/opencart from 0.0.0. An SQL Injection issue was identified in the Divido payment extension for OpenCart, which is included by default in version 3.0.3.9. As an anonymous unauthenticated user, if the Divido payment module is installed (it does not have to be enabled), it is possible to exploit SQL injection to gain unauthorised access to the backend database. For any site which is vulnerable, any unauthenticated user could exploit this to dump the entire OpenCart database, including customer PII data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21514
- https://github.com/opencart/opencart/commit/46bd5f5a8056ff9aad0aa7d71729c4cf593d67e2
- https://github.com/opencart/opencart
- https://github.com/opencart/opencart/blob/3.0.3.9/upload/catalog/model/extension/payment/divido.php%23L114
- https://security.snyk.io/vuln/SNYK-PHP-OPENCARTOPENCART-7266565
