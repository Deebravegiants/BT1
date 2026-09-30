# [H] Django Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-9jmf-237g-qf46
CVE: CVE-2024-39330
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-9jmf-237g-qf46
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.0 <5.0.7
- PyPI: `Django` — affected >=4.2 <4.2.14

## Details
An issue was discovered in Django 5.0 before 5.0.7 and 4.2 before 4.2.14. Derived classes of the `django.core.files.storage.Storage` base class, when they override `generate_filename()` without replicating the file-path validations from the parent class, potentially allow directory traversal via certain inputs during a `save()` call. (Built-in Storage sub-classes are unaffected.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39330
- https://github.com/django/django/commit/2b00edc0151a660d1eb86da4059904a0fc4e095e
- https://github.com/django/django/commit/9f4f63e9ebb7bf6cb9547ee4e2526b9b96703270
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-58.yaml
- https://groups.google.com/forum/#%21forum/django-announce
- https://security.netapp.com/advisory/ntap-20240808-0005
- https://www.djangoproject.com/weblog/2024/jul/09/security-releases
