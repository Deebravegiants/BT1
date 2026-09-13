# [C] SQL Injection in Django

## Summary
Severity: Critical
Advisory: GHSA-2gwj-7jmv-h26r
CVE: CVE-2022-28346
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-2gwj-7jmv-h26r
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.28
- PyPI: `Django` — affected >=3.2 <3.2.13
- PyPI: `Django` — affected >=4.0 <4.0.4

## Details
An issue was discovered in Django 2.2 before 2.2.28, 3.2 before 3.2.13, and 4.0 before 4.0.4. `QuerySet.annotate()`, `aggregate()`, and `extra()` methods are subject to SQL injection in column aliases via a crafted dictionary (with dictionary expansion) as the passed `**kwargs`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28346
- https://github.com/django/django/commit/2044dac5c6968441be6f534c4139bcf48c5c7e48
- https://github.com/django/django/commit/2c09e68ec911919360d5f8502cefc312f9e03c5d
- https://github.com/django/django/commit/800828887a0509ad1162d6d407e94d8de7eafc60
- https://github.com/django/django/commit/93cae5cb2f9a4ef1514cf1a41f714fef08005200
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/advisories/GHSA-2gwj-7jmv-h26r
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-190.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.debian.org/debian-lts-announce/2022/04/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://security.netapp.com/advisory/ntap-20220609-0002
- https://www.debian.org/security/2022/dsa-5254
- https://www.djangoproject.com/weblog/2022/apr/11/security-releases
- http://www.openwall.com/lists/oss-security/2022/04/11/1
