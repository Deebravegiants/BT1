# [M] BIT-django-2025-59682

## Summary
Severity: Medium
Advisory: BIT-django-2025-59682
Aliases: CVE-2025-59682, GHSA-q95w-c7qg-hrff, PYSEC-2026-1296
Ecosystem: Bitnami
Published: 2025-10-23
Source: https://osv.dev/vulnerability/BIT-django-2025-59682
Type: osv

## Affected
- Bitnami: `django` — affected >=5.2.0 <5.2.7

## Details
An issue was discovered in Django 4.2 before 4.2.25, 5.1 before 5.1.13, and 5.2 before 5.2.7. The django.utils.archive.extract() function, used by the "startapp --template" and "startproject --template" commands, allows partial directory traversal via an archive with file paths sharing a common prefix with the target directory.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2025-59682
- https://www.djangoproject.com/weblog/2025/oct/01/security-releases/
- http://www.openwall.com/lists/oss-security/2025/10/01/3
