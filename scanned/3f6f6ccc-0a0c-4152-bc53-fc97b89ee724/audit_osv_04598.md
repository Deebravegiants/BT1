# [H] Potential denial-of-service vulnerability in django.utils.text.Truncator HTML methods

## Summary
Severity: High
Advisory: BIT-django-2026-1285
Aliases: CVE-2026-1285, GHSA-4rrr-2h4v-f3j9, PYSEC-2026-45
Ecosystem: Bitnami
Published: 2026-02-05
Source: https://osv.dev/vulnerability/BIT-django-2026-1285
Type: osv

## Affected
- Bitnami: `django` — affected >=6.0.0 <6.0.2

## Details
An issue was discovered in 6.0 before 6.0.2, 5.2 before 5.2.11, and 4.2 before 4.2.28.
`django.utils.text.Truncator.chars()` and `Truncator.words()` methods (with `html=True`) and the `truncatechars_html` and `truncatewords_html` template filters allow a remote attacker to cause a potential denial-of-service via crafted inputs containing a large number of unmatched HTML end tags.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Seokchan Yoon for reporting this issue.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/g/django-announce
- https://nvd.nist.gov/vuln/detail/CVE-2026-1285
- https://www.djangoproject.com/weblog/2026/feb/03/security-releases/
