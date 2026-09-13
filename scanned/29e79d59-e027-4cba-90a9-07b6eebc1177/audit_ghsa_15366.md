# [M] Django vulnerable to a denial-of-service attack

## Summary
Severity: Medium
Advisory: GHSA-795c-9xpc-xw6g
CVE: CVE-2024-41990
CWE: CWE-130
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-07
Source: https://github.com/advisories/GHSA-795c-9xpc-xw6g
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.0 <5.0.8
- PyPI: `Django` — affected >=4.2 <4.2.15

## Details
An issue was discovered in Django 5.0 before 5.0.8 and 4.2 before 4.2.15. The urlize() and urlizetrunc() template filters are subject to a potential denial-of-service attack via very large inputs with a specific sequence of characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41990
- https://github.com/django/django/commit/7b7b909579c8311c140c89b8a9431bf537febf93
- https://github.com/django/django/commit/d0a82e26a74940bf0c78204933c3bdd6a283eb88
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-68.yaml
- https://groups.google.com/forum/#%21forum/django-announce
- https://security.netapp.com/advisory/ntap-20240905-0007
- https://www.djangoproject.com/weblog/2024/aug/06/security-releases
