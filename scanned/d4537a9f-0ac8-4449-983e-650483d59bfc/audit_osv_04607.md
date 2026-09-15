# [M] Potential exposure of private data via cached Set-Cookie response

## Summary
Severity: Medium
Advisory: BIT-django-2026-48588
Aliases: CVE-2026-48588, GHSA-3h9f-r86x-qvjx, PYSEC-2026-2090
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-django-2026-48588
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.7

## Details
An issue was discovered in Django 6.0 before 6.0.7 and 5.2 before 5.2.16.
`UpdateCacheMiddleware` and the `cache_page()` decorator cache responses that vary on cookies when the incoming request carries unrelated cookies, which allows remote attackers to read private data from the shared cache.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Chris Whyland for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-48588
- https://www.djangoproject.com/weblog/2026/jul/07/security-releases/
