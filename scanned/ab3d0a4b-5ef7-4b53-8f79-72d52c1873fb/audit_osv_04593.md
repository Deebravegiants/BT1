# [H] BIT-django-2025-26699

## Summary
Severity: High
Advisory: BIT-django-2025-26699
Aliases: CVE-2025-26699, GHSA-p3fp-8748-vqfq, PYSEC-2025-13
Ecosystem: Bitnami
Published: 2025-03-10
Source: https://osv.dev/vulnerability/BIT-django-2025-26699
Type: osv

## Affected
- Bitnami: `django` — affected >=4.2.0 <5.1.7

## Details
An issue was discovered in Django 5.1 before 5.1.7, 5.0 before 5.0.13, and 4.2 before 4.2.20. The django.utils.text.wrap() method and wordwrap template filter are subject to a potential denial-of-service attack when used with very long strings.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2025/mar/06/security-releases/
- http://www.openwall.com/lists/oss-security/2025/03/06/12
- https://lists.debian.org/debian-lts-announce/2025/03/msg00012.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-26699
