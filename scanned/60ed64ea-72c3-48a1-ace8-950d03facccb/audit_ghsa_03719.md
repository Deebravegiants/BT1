# [M] Django open redirect and possible XSS attack via user-supplied numeric redirect URLs

## Summary
Severity: Medium
Advisory: GHSA-37hp-765x-j95x
CVE: CVE-2017-7233
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-37hp-765x-j95x
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.10a1 <1.10.7
- PyPI: `Django` — affected >=1.9a1 <1.9.13
- PyPI: `Django` — affected >=1.8a1 <1.8.18

## Details
Django 1.10 before 1.10.7, 1.9 before 1.9.13, and 1.8 before 1.8.18 relies on user input in some cases to redirect the user to an "on success" URL. The security check for these redirects (namely ``django.utils.http.is_safe_url()``) considered some numeric URLs "safe" when they shouldn't be, aka an open redirect vulnerability. Also, if a developer relies on ``is_safe_url()`` to provide safe redirect targets and puts such a URL into a link, they could suffer from an XSS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7233
- https://github.com/django/django/commit/254326cb3682389f55f886804d2c43f7b9f23e4f
- https://github.com/django/django/commit/8339277518c7d8ec280070a780915304654e3b66
- https://github.com/django/django/commit/f824655bc2c50b19d2f202d7640785caabc82787
- https://access.redhat.com/errata/RHSA-2017:1445
- https://access.redhat.com/errata/RHSA-2017:1451
- https://access.redhat.com/errata/RHSA-2017:1462
- https://access.redhat.com/errata/RHSA-2017:1470
- https://access.redhat.com/errata/RHSA-2017:1596
- https://access.redhat.com/errata/RHSA-2017:3093
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/advisories/GHSA-37hp-765x-j95x
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2017-9.yaml
- https://www.djangoproject.com/weblog/2017/apr/04/security-releases
- http://www.debian.org/security/2017/dsa-3835
