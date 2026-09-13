# [C] SQL Injection in Django

## Summary
Severity: Critical
Advisory: GHSA-w24h-v9qh-8gxj
CVE: CVE-2022-28347
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-w24h-v9qh-8gxj
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.28
- PyPI: `Django` — affected >=3.2 <3.2.13
- PyPI: `Django` — affected >=4.0 <4.0.4

## Details
A SQL injection issue was discovered in `QuerySet.explain()` in Django 2.2 before 2.2.28, 3.2 before 3.2.13, and 4.0 before 4.0.4. This occurs by passing a crafted dictionary (with dictionary expansion) as the `**options` argument, and placing the injection payload in an option name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28347
- https://github.com/django/django/commit/00b0fc50e1738c7174c495464a5ef069408a4402
- https://github.com/django/django/commit/29a6c98b4c13af82064f993f0acc6e8fafa4d3f5
- https://github.com/django/django/commit/6723a26e59b0b5429a0c5873941e01a2e1bdbb81
- https://github.com/django/django/commit/9e19accb6e0a00ba77d5a95a91675bf18877c72d
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/advisories/GHSA-w24h-v9qh-8gxj
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-191.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://www.debian.org/security/2022/dsa-5254
- https://www.djangoproject.com/weblog/2022/apr/11/security-releases
- http://www.openwall.com/lists/oss-security/2022/04/11/1
