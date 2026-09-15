# [C] django-s3file is vulnerable to relative path traversal

## Summary
Severity: Critical
Advisory: GHSA-67qg-7284-2277
CVE: CVE-2026-42196
CWE: CWE-22, CWE-23, CWE-26
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-67qg-7284-2277
Type: github-advisory

## Affected
- PyPI: `django-s3file` — affected >=0 <7.0.2

## Details
### Impact
`S3FileMiddleware` is vulnerable to relative path traversal attacks, where an attacker can use a modified request to escape pre-signed upload locations and have the Django application load files from random locations into `request.FILES`

Depending on how files are handled, this may lead to confidentiality and integrity issues.

### Patches
Django-S3File urges all users to update to a patched version >=7.0.2.

## References
- https://github.com/codingjoe/django-s3file/security/advisories/GHSA-67qg-7284-2277
- https://nvd.nist.gov/vuln/detail/CVE-2026-42196
- https://github.com/codingjoe/django-s3file
