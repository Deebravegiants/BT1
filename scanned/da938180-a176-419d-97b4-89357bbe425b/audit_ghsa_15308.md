# [M] Django memory consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jh75-99hh-qvx9
CVE: CVE-2024-41989
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-07
Source: https://github.com/advisories/GHSA-jh75-99hh-qvx9
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.0 <5.0.8
- PyPI: `Django` — affected >=4.2 <4.2.15

## Details
An issue was discovered in Django 5.0 before 5.0.8 and 4.2 before 4.2.15. The floatformat template filter is subject to significant memory consumption when given a string representation of a number in scientific notation with a large exponent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41989
- https://github.com/django/django/commit/27900fe56f3d3cabb4aeb6ccb82f92bab29073a8
- https://github.com/django/django/commit/fc76660f589ac07e45e9cd34ccb8087aeb11904b
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-67.yaml
- https://groups.google.com/forum/#%21forum/django-announce
- https://security.netapp.com/advisory/ntap-20240905-0007
- https://www.djangoproject.com/weblog/2024/aug/06/security-releases
