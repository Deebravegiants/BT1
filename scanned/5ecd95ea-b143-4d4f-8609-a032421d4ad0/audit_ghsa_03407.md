# [M] Directory Traversal in Django

## Summary
Severity: Medium
Advisory: GHSA-xgxc-v2qg-chmh
CVE: CVE-2021-28658
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-04-08
Source: https://github.com/advisories/GHSA-xgxc-v2qg-chmh
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2a1 <2.2.20
- PyPI: `Django` — affected >=3.0a1 <3.0.14
- PyPI: `Django` — affected >=3.1a1 <3.1.8

## Details
In Django 2.2 before 2.2.20, 3.0 before 3.0.14, and 3.1 before 3.1.8, MultiPartParser allowed directory traversal via uploaded files with suitably crafted file names. Built-in upload handlers were not affected by this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28658
- https://docs.djangoproject.com/en/3.1/releases/security
- https://github.com/advisories/GHSA-xgxc-v2qg-chmh
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-6.yaml
- https://groups.google.com/g/django-announce/c/ePr5j-ngdPU
- https://lists.debian.org/debian-lts-announce/2021/04/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZVKYPHR3TKR2ESWXBPOJEKRO2OSJRZUE
- https://pypi.org/project/Django
- https://security.netapp.com/advisory/ntap-20210528-0001
- https://www.djangoproject.com/weblog/2021/apr/06/security-releases
