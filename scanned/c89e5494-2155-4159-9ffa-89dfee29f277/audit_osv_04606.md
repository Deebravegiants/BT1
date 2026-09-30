# [M] Potential exposure of private data via whitespace padding in Vary header

## Summary
Severity: Medium
Advisory: BIT-django-2026-48587
Aliases: CVE-2026-48587, GHSA-923m-gv2p-w5qp, PYSEC-2026-198
Ecosystem: Bitnami
Published: 2026-06-06
Source: https://osv.dev/vulnerability/BIT-django-2026-48587
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.6

## Details
An issue was discovered in Django 5.2 before 5.2.15 and 6.0 before 6.0.6.
`django.utils.cache.has_vary_header()` in Django does not strip leading or trailing whitespace from `Vary` response header values before comparison, which allows remote attackers to read cached responses via requests to URLs whose responses contain whitespace-padded Vary header values.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Navid Rezazadeh for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-48587
- https://www.djangoproject.com/weblog/2026/jun/03/security-releases/
