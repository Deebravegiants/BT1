# [H] Django is subject to SQL injection through its column aliases

## Summary
Severity: High
Advisory: GHSA-6w2r-r2m5-xq5w
CVE: CVE-2025-57833
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-6w2r-r2m5-xq5w
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <4.2.24
- PyPI: `Django` — affected >=5.0a1 <5.1.12
- PyPI: `Django` — affected >=5.2a1 <5.2.6

## Details
An issue was discovered in Django 4.2 before 4.2.24, 5.1 before 5.1.12, and 5.2 before 5.2.6. FilteredRelation is subject to SQL injection in column aliases, using a suitably crafted dictionary, with dictionary expansion, as the **kwargs passed QuerySet.annotate() or QuerySet.alias().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57833
- https://github.com/django/django/commit/102965ea93072fe3c39a30be437c683ec1106ef5
- https://github.com/django/django/commit/31334e6965ad136a5e369993b01721499c5d1a92
- https://github.com/django/django/commit/4c044fcc866ec226f612c475950b690b0139d243
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2025-105.yaml
- https://groups.google.com/g/django-announce
- https://lists.debian.org/debian-lts-announce/2025/09/msg00017.html
- https://medium.com/@EyalSec/django-unauthenticated-0-click-rce-and-sql-injection-using-default-configuration-059964f3f898
- https://www.djangoproject.com/weblog/2025/sep/03/security-releases
- http://www.openwall.com/lists/oss-security/2025/09/03/3
