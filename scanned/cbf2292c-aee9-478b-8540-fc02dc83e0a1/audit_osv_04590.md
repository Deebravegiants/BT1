# [H] BIT-django-2024-53907

## Summary
Severity: High
Advisory: BIT-django-2024-53907
Aliases: CVE-2024-53907, GHSA-8498-2h75-472j, PYSEC-2024-156
Ecosystem: Bitnami
Published: 2025-03-10
Source: https://osv.dev/vulnerability/BIT-django-2024-53907
Type: osv

## Affected
- Bitnami: `django` — affected >=5.0.0 <5.1.4

## Details
An issue was discovered in Django 5.1 before 5.1.4, 5.0 before 5.0.10, and 4.2 before 4.2.17. The strip_tags() method and striptags template filter are subject to a potential denial-of-service attack via certain inputs containing large sequences of nested incomplete HTML entities.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://www.openwall.com/lists/oss-security/2024/12/04/3
- https://lists.debian.org/debian-lts-announce/2024/12/msg00028.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-53907
