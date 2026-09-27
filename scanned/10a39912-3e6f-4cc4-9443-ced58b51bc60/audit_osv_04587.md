# [H] BIT-django-2024-38875

## Summary
Severity: High
Advisory: BIT-django-2024-38875
Aliases: CVE-2024-38875, GHSA-qg2p-9jwr-mmqf, PYSEC-2024-56
Ecosystem: Bitnami
Published: 2025-03-10
Source: https://osv.dev/vulnerability/BIT-django-2024-38875
Type: osv

## Affected
- Bitnami: `django` — affected >=5.0.0 <5.0.7

## Details
An issue was discovered in Django 4.2 before 4.2.14 and 5.0 before 5.0.7. urlize and urlizetrunc were subject to a potential denial of service attack via certain inputs with a very large number of brackets.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/forum/#%21forum/django-announce
- https://www.djangoproject.com/weblog/2024/jul/09/security-releases/
- https://nvd.nist.gov/vuln/detail/CVE-2024-38875
- https://security.netapp.com/advisory/ntap-20240808-0005/
