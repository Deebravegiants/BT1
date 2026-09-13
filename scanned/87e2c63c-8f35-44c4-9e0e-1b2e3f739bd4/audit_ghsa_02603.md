# [C] SQL Injection in Django

## Summary
Severity: Critical
Advisory: GHSA-xpfp-f569-q3p2
CVE: CVE-2021-35042
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-xpfp-f569-q3p2
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2a1 <3.2.5
- PyPI: `Django` — affected >=3.0a1 <3.1.13

## Details
Django 3.1.x before 3.1.13 and 3.2.x before 3.2.5 allows QuerySet.order_by SQL injection if order_by is untrusted input from a client of a web application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-35042
- https://github.com/django/django/commit/0bd57a879a0d54920bb9038a732645fb917040e9
- https://github.com/django/django/commit/a34a5f724c5d5adb2109374ba3989ebb7b11f81f
- https://github.com/django/django/commit/dae83a24519d6f284c74414e0b81d64d9b5a0db4
- https://docs.djangoproject.com/en/3.2/releases/security
- https://github.com/advisories/GHSA-xpfp-f569-q3p2
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-109.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SS6NJTBYWOX6J7G4U3LUOILARJKWPQ5Y
- https://security.netapp.com/advisory/ntap-20210805-0008
- https://www.djangoproject.com/weblog/2021/jul/01/security-releases
- https://www.openwall.com/lists/oss-security/2021/07/02/2
