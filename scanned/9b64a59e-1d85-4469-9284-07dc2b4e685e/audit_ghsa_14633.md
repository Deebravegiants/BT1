# [H] Django SQL injection in HasKey(lhs, rhs) on Oracle

## Summary
Severity: High
Advisory: GHSA-m9g8-fxxm-xg86
CVE: CVE-2024-53908
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-06
Source: https://github.com/advisories/GHSA-m9g8-fxxm-xg86
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.0.0 <5.0.10
- PyPI: `Django` — affected >=5.1.0 <5.1.4
- PyPI: `Django` — affected >=4.2.0 <4.2.17
- PyPI: `django` — affected >=5.1 <5.1.4
- PyPI: `django` — affected >=5.0 <5.0.10
- PyPI: `django` — affected >=4.2 <4.2.17

## Details
An issue was discovered in Django 5.1 before 5.1.4, 5.0 before 5.0.10, and 4.2 before 4.2.17. Direct usage of the django.db.models.fields.json.HasKey lookup, when an Oracle database is used, is subject to SQL injection if untrusted data is used as an lhs value. (Applications that use the jsonfield.has_key lookup via __ are unaffected.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53908
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-157.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2024/dec/04/security-releases
- https://www.openwall.com/lists/oss-security/2024/12/04/3
