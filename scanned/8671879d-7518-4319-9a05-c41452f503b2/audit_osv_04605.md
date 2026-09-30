# [C] Privilege abuse in GenericInlineModelAdmin

## Summary
Severity: Critical
Advisory: BIT-django-2026-4277
Aliases: CVE-2026-4277, GHSA-pwjp-ccjc-ghwg, PYSEC-2026-52
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-django-2026-4277
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.4

## Details
An issue was discovered in 6.0 before 6.0.4, 5.2 before 5.2.13, and 4.2 before 4.2.30.
Add permissions on inline model instances were not validated on submission of
forged `POST` data in `GenericInlineModelAdmin`.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank N05ec@LZU-DSLab for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-4277
- https://www.djangoproject.com/weblog/2026/apr/07/security-releases/
