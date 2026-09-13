# [M] Username enumeration through timing difference in mod_wsgi authentication handler

## Summary
Severity: Medium
Advisory: BIT-django-2025-13473
Aliases: CVE-2025-13473, GHSA-2mcm-79hx-8fxw, PYSEC-2026-42
Ecosystem: Bitnami
Published: 2026-02-05
Source: https://osv.dev/vulnerability/BIT-django-2025-13473
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.2

## Details
An issue was discovered in 6.0 before 6.0.2, 5.2 before 5.2.11, and 4.2 before 4.2.28.
The `django.contrib.auth.handlers.modwsgi.check_password()` function for authentication via `mod_wsgi` allows remote attackers to enumerate users via a timing attack.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Stackered for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2025-13473
- https://www.djangoproject.com/weblog/2026/feb/03/security-releases/
