# [H] Potential denial-of-service vulnerability via repeated headers when using ASGI

## Summary
Severity: High
Advisory: BIT-django-2025-14550
Aliases: CVE-2025-14550, GHSA-33mw-q7rj-mjwj, PYSEC-2026-43
Ecosystem: Bitnami
Published: 2026-02-05
Source: https://osv.dev/vulnerability/BIT-django-2025-14550
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.2

## Details
An issue was discovered in 6.0 before 6.0.2, 5.2 before 5.2.11, and 4.2 before 4.2.28.
`ASGIRequest` allows a remote attacker to cause a potential denial-of-service via a crafted request with multiple duplicate headers.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Jiyong Yang for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2025-14550
- https://www.djangoproject.com/weblog/2026/feb/03/security-releases/
