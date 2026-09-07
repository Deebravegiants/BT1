# [H] Pagekit File Upload vulnerability

## Summary
Severity: High
Advisory: GHSA-692x-89xv-64jx
CVE: CVE-2019-19013
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-692x-89xv-64jx
Type: github-advisory

## Affected
- Packagist: `pagekit/pagekit` — affected >=0

## Details
A CSRF vulnerability in Pagekit 1.0.17 allows an attacker to upload an arbitrary file by removing the CSRF token from a request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19013
- https://github.com/pagekit/pagekit
- https://gitlab.com/gitlab-org/security-products/gemnasium-db/-/commit/fdf885ccf7c57c69f4d256bbb3ec76a927267a2b
- https://packetstormsecurity.com/files/155426/Pagekit-CMS-1.0.17-Cross-Site-Request-Forgery.html
