# [M] Signed cookie salt namespace collision in django.http.HttpRequest.get_signed_cookie

## Summary
Severity: Medium
Advisory: BIT-django-2026-6873
Aliases: CVE-2026-6873, GHSA-h7pc-vwp9-298g, PYSEC-2026-199
Ecosystem: Bitnami
Published: 2026-06-06
Source: https://osv.dev/vulnerability/BIT-django-2026-6873
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.6

## Details
An issue was discovered in Django 6.0 before 6.0.6 and 5.2 before 5.2.15.
`django.http.HttpRequest.get_signed_cookie` in Django uses a non-injective salt derivation (concatenating the cookie name and salt argument), which allows a remote attacker to use a cookie in a context different from the one where it was signed, via distinct `(name, salt)` pairs that produce the same concatenation.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Peng Zhou for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-6873
- https://www.djangoproject.com/weblog/2026/jun/03/security-releases/
