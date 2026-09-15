# [M] Potential exposure of private data due to incorrect handling of Vary: * in UpdateCacheMiddleware

## Summary
Severity: Medium
Advisory: BIT-django-2026-6907
Aliases: CVE-2026-6907, GHSA-5hrc-gvxj-w55p, PYSEC-2026-55
Ecosystem: Bitnami
Published: 2026-05-08
Source: https://osv.dev/vulnerability/BIT-django-2026-6907
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.5

## Details
An issue was discovered in 6.0 before 6.0.5 and 5.2 before 5.2.14.
`django.middleware.cache.UpdateCacheMiddleware` erroneously caches requests where the `Vary` header contained an asterisk (`'*'`). This can lead to private data being stored and served.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Ahmad Sadeddin for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-6907
- https://www.djangoproject.com/weblog/2026/may/05/security-releases/
