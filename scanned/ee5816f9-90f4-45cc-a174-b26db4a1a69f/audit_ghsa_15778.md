# [M] Django vulnerable to user enumeration attack

## Summary
Severity: Medium
Advisory: GHSA-x7q2-wr7g-xqmf
CVE: CVE-2024-39329
CWE: CWE-208
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-x7q2-wr7g-xqmf
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.0 <5.0.7
- PyPI: `Django` — affected >=4.2 <4.2.14

## Details
An issue was discovered in Django 5.0 before 5.0.7 and 4.2 before 4.2.14. The `django.contrib.auth.backends.ModelBackend.authenticate()` method allows remote attackers to enumerate users via a timing attack involving login requests for users with an unusable password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39329
- https://github.com/django/django/commit/07cefdee4a9d1fcd9a3a631cbd07c78defd1923b
- https://github.com/django/django/commit/156d3186c96e3ec2ca73b8b25dc2ef366e38df14
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-57.yaml
- https://groups.google.com/forum/#%21forum/django-announce
- https://security.netapp.com/advisory/ntap-20240808-0005
- https://www.djangoproject.com/weblog/2024/jul/09/security-releases
