# [M] django-allauth's Okta and NetIQ implementations used a mutable identifier for authorization decisions

## Summary
Severity: Medium
Advisory: GHSA-8m3c-c723-h4p4
CVE: CVE-2025-65431
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-8m3c-c723-h4p4
Type: github-advisory

## Affected
- PyPI: `django-allauth` — affected >=0 <65.13.0

## Details
An issue was discovered in allauth-django before 65.13.0. Both Okta and NetIQ were using preferred_username as the identifier for third-party provider accounts. That value may be mutable and should therefore be avoided for authorization decisions. The providers are now using sub instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65431
- https://github.com/pennersr/django-allauth/commit/8feef46e0e07b25fc5594c8f268afa247ebc3412
- https://allauth.org/news/2025/10/django-allauth-65.13.0-released
- https://codeberg.org/allauth/django-allauth
- https://github.com/pypa/advisory-database/tree/main/vulns/django-allauth/PYSEC-2025-111.yaml
