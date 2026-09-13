# [H] BIT-django-2024-45230

## Summary
Severity: High
Advisory: BIT-django-2024-45230
Aliases: CVE-2024-45230, GHSA-5hgc-2vfp-mqvc, PYSEC-2024-102
Ecosystem: Bitnami
Published: 2024-10-19
Source: https://osv.dev/vulnerability/BIT-django-2024-45230
Type: osv

## Affected
- Bitnami: `django` — affected >=5.1.0 <5.2.5

## Details
An issue was discovered in Django 5.1 before 5.1.1, 5.0 before 5.0.9, and 4.2 before 4.2.16. The urlize() and urlizetrunc() template filters are subject to a potential denial-of-service attack via very large inputs with a specific sequence of characters.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/forum/#%21forum/django-announce
- https://www.djangoproject.com/weblog/2024/sep/03/security-releases/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45230
