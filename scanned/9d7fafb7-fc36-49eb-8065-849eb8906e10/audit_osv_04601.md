# [M] Potential denial-of-service vulnerability in check_for_language()

## Summary
Severity: Medium
Advisory: BIT-django-2026-15337
Aliases: CVE-2026-15337
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-django-2026-15337
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.8

## Details
An issue was discovered in Django 5.2 before 5.2.17 and 6.0 before 6.0.8.
`django.utils.translation.check_for_language()` is subject to a potential denial-of-service attack when given many distinct, very long language codes, which are retained as keys in an in-memory cache and consume process memory. Such codes reach the function through the `django.views.i18n.set_language()` view, which is not routed by default. The consumed memory is bounded, since request data is limited by the `DATA_UPLOAD_MAX_MEMORY_SIZE` setting (default 2.5 MB) and the cache holds a fixed maximum number of entries.
Earlier, unsupported Django series (such as 5.1.x, 5.0.x, and 4.2.x) were not evaluated and may also be affected.
Django would like to thank Jaeyoung Jang for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://github.com/django/django/commit/224dbc832586ad5cfb0237c2ff30d14baeaddc6f
- https://github.com/django/django/commit/27137e655e442e81095f1f8f77ff3870d9fdf169
- https://github.com/django/django/commit/5b3523d29be25948e1dd90b3863a002f00fc865f
- https://github.com/django/django/commit/c72a5dbb64d0777f3f471f1be94e8b2ca91e0959
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-15337
- https://www.djangoproject.com/weblog/2026/aug/04/security-releases/
