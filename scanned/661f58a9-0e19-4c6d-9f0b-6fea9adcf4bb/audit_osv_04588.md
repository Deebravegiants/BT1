# [H] BIT-django-2024-41991

## Summary
Severity: High
Advisory: BIT-django-2024-41991
Aliases: CVE-2024-41991, GHSA-r836-hh6v-rg5g, PYSEC-2024-69
Ecosystem: Bitnami
Published: 2024-08-08
Source: https://osv.dev/vulnerability/BIT-django-2024-41991
Type: osv

## Affected
- Bitnami: `django` — affected >=5.0.0 <5.0.8

## Details
An issue was discovered in Django 5.0 before 5.0.8 and 4.2 before 4.2.15. The urlize and urlizetrunc template filters, and the AdminURLFieldWidget widget, are subject to a potential denial-of-service attack via certain inputs with a very large number of Unicode characters.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/forum/#%21forum/django-announce
- https://www.djangoproject.com/weblog/2024/aug/06/security-releases/
- https://nvd.nist.gov/vuln/detail/CVE-2024-41991
- https://security.netapp.com/advisory/ntap-20240905-0007/
