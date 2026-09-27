# [M] Potential exposure of private data via case-sensitive Cache-Control directives in UpdateCacheMiddleware

## Summary
Severity: Medium
Advisory: BIT-django-2026-8404
Aliases: CVE-2026-8404, GHSA-8cjm-8mp7-r2xf, PYSEC-2026-201
Ecosystem: Bitnami
Published: 2026-06-06
Source: https://osv.dev/vulnerability/BIT-django-2026-8404
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.6

## Details
An issue was discovered in Django 5.2 before 5.2.15 and 6.0 before 6.0.6.
`django.middleware.cache.UpdateCacheMiddleware` in Django does not match `Cache-Control` response directives case-insensitively, which allows remote attackers to read responses that were incorrectly cached because their `Cache-Control` directives used uppercase or mixed-case values.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Ahmed Badawe for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-8404
- https://www.djangoproject.com/weblog/2026/jun/03/security-releases/
