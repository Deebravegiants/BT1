# [M] BIT-django-2025-32873

## Summary
Severity: Medium
Advisory: BIT-django-2025-32873
Aliases: CVE-2025-32873, GHSA-8j24-cjrq-gr2m, PYSEC-2025-37
Ecosystem: Bitnami
Published: 2025-06-18
Source: https://osv.dev/vulnerability/BIT-django-2025-32873
Type: osv

## Affected
- Bitnami: `django` — affected >=5.2.0 <5.2.5

## Details
An issue was discovered in Django 4.2 before 4.2.21, 5.1 before 5.1.9, and 5.2 before 5.2.1. The django.utils.html.strip_tags() function is vulnerable to a potential denial-of-service (slow performance) when processing inputs containing large sequences of incomplete HTML tags. The template filter striptags is also vulnerable, because it is built on top of strip_tags().

## References
- http://www.openwall.com/lists/oss-security/2025/05/07/1
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2025-32873
- https://www.djangoproject.com/weblog/2025/may/07/security-releases/
