# [M] Dcat-Admin Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-37x3-j9jq-vrjx
CVE: CVE-2024-54775
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-12-28
Source: https://github.com/advisories/GHSA-37x3-j9jq-vrjx
Type: github-advisory

## Affected
- Packagist: `dcat/laravel-admin` — affected 2.2.0-beta
- Packagist: `dcat/laravel-admin` — affected 2.2.2-beta

## Details
Dcat-Admin v2.2.0-beta and v2.2.2-beta contains a Cross-Site Scripting (XSS) vulnerability via /admin/auth/menu and /admin/auth/extensions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-54775
- https://github.com/taynes-llllzt/taynes/issues/5
- https://github.com/jqhph/dcat-admin
