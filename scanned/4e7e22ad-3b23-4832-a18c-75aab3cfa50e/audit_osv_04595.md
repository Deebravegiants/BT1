# [C] BIT-django-2025-59681

## Summary
Severity: Critical
Advisory: BIT-django-2025-59681
Aliases: CVE-2025-59681, GHSA-hpr9-3m2g-3j9p, PYSEC-2025-106
Ecosystem: Bitnami
Published: 2025-10-08
Source: https://osv.dev/vulnerability/BIT-django-2025-59681
Type: osv

## Affected
- Bitnami: `django` — affected >=5.2.0 <5.2.7

## Details
An issue was discovered in Django 4.2 before 4.2.25, 5.1 before 5.1.13, and 5.2 before 5.2.7. QuerySet.annotate(), QuerySet.alias(), QuerySet.aggregate(), and QuerySet.extra() are subject to SQL injection in column aliases, when using a suitably crafted dictionary, with dictionary expansion, as the **kwargs passed to these methods (on MySQL and MariaDB).

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2025-59681
- https://www.djangoproject.com/weblog/2025/oct/01/security-releases/
- http://www.openwall.com/lists/oss-security/2025/10/01/3
