# [M] django-allauth does not reject access tokens for inactive users

## Summary
Severity: Medium
Advisory: GHSA-qhmc-3mvr-f2j4
CVE: CVE-2025-65430
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-qhmc-3mvr-f2j4
Type: github-advisory

## Affected
- PyPI: `django-allauth` — affected >=0 <65.13.0

## Details
An issue was discovered in allauth-django before 65.13.0. IdP: marking a user as is_active=False after having handed tokens for that user while the account was still active had no effect. Fixed the access/refresh tokens are now rejected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65430
- https://github.com/pennersr/django-allauth/commit/39f4a4ce9c891795b00914ca5ec32de72d5369c0
- https://github.com/pennersr/django-allauth/commit/c54edf947c5a1c8c4ff3cddb75c86000ecb2507d
- https://allauth.org/news/2025/10/django-allauth-65.13.0-released
- https://codeberg.org/allauth/django-allauth
- https://github.com/pypa/advisory-database/tree/main/vulns/django-allauth/PYSEC-2025-110.yaml
