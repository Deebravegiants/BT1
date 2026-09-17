# [H] Django vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-f6f8-9mx6-9mx2
CVE: CVE-2024-39614
CWE: CWE-130, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-f6f8-9mx6-9mx2
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.0 <5.0.7
- PyPI: `Django` — affected >=4.2 <4.2.14

## Details
An issue was discovered in Django 5.0 before 5.0.7 and 4.2 before 4.2.14. `get_supported_language_variant()` was subject to a potential denial-of-service attack when used with very long strings containing specific characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39614
- https://github.com/django/django/commit/17358fb35fb7217423d4c4877ccb6d1a3a40b1c3
- https://github.com/django/django/commit/8e7a44e4bec0f11474699c3111a5e0a45afe7f49
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-59.yaml
- https://groups.google.com/forum/#%21forum/django-announce
- https://security.netapp.com/advisory/ntap-20240808-0005
- https://www.djangoproject.com/weblog/2024/jul/09/security-releases
