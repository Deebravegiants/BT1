# [M] Django Directory Traversal via archive.extract

## Summary
Severity: Medium
Advisory: GHSA-fvgf-6h6h-3322
CVE: CVE-2021-3281
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-03-18
Source: https://github.com/advisories/GHSA-fvgf-6h6h-3322
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.18
- PyPI: `Django` — affected >=3.1 <3.1.6
- PyPI: `Django` — affected >=3.0 <3.0.12

## Details
In Django 2.2 before 2.2.18, 3.0 before 3.0.12, and 3.1 before 3.1.6, the django.utils.archive.extract method (used by "startapp --template" and "startproject --template") allows directory traversal via an archive with absolute paths or relative paths with dot segments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3281
- https://github.com/django/django/commit/02e6592835b4559909aa3aaaf67988fef435f624
- https://github.com/django/django/commit/05413afa8c18cdb978fcdf470e09f7a12b234a23
- https://github.com/django/django/commit/21e7622dec1f8612c85c2fc37fe8efbfd3311e37
- https://github.com/django/django/commit/52e409ed17287e9aabda847b6afe58be2fa9f86a
- https://docs.djangoproject.com/en/3.1/releases/3.0.12
- https://docs.djangoproject.com/en/3.1/releases/security
- https://github.com/advisories/GHSA-fvgf-6h6h-3322
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-9.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YF52FKEH5S2P5CM4X7IXSYG67YY2CDOO
- https://security.netapp.com/advisory/ntap-20210226-0004
- https://www.djangoproject.com/weblog/2021/feb/01/security-releases
