# [M] Django data leakage via querystring manipulation in admin

## Summary
Severity: Medium
Advisory: GHSA-rw75-m7gp-92m3
CVE: CVE-2014-0483
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rw75-m7gp-92m3
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.14
- PyPI: `Django` — affected >=1.5 <1.5.9
- PyPI: `Django` — affected >=1.6 <1.6.6
- PyPI: `Django` — affected >=1.7a1 <1.7c3

## Details
The administrative interface (contrib.admin) in Django before 1.4.14, 1.5.x before 1.5.9, 1.6.x before 1.6.6, and 1.7 before release candidate 3 does not check if a field represents a relationship between models, which allows remote authenticated users to obtain sensitive information via a to_field parameter in a popup action to an admin change form page, as demonstrated by a `/admin/auth/user/?pop=1&t=password` URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0483
- https://github.com/django/django/commit/027bd348642007617518379f8b02546abacaa6e0
- https://github.com/django/django/commit/2a446c896e7c814661fb9c4f212b071b2a7fa446
- https://github.com/django/django/commit/2b31342cdf14fc20e07c43d258f1e7334ad664a6
- https://github.com/django/django/commit/f7c494f2506250b8cb5923714360a3642ed63e0f
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2014-7.yaml
- https://web.archive.org/web/20151016194735/http://secunia.com/advisories/61276
- https://web.archive.org/web/20151016202523/http://secunia.com/advisories/59782
- https://web.archive.org/web/20151023143840/http://secunia.com/advisories/61281
- https://www.djangoproject.com/weblog/2014/aug/20/security
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00023.html
- http://www.debian.org/security/2014/dsa-3010
