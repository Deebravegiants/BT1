# [C] Django `Trunc()` and `Extract()` database functions vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-p64x-8rxx-wf6q
CVE: CVE-2022-34265
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-05
Source: https://github.com/advisories/GHSA-p64x-8rxx-wf6q
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2a1 <3.2.14
- PyPI: `Django` — affected >=4.0a1 <4.0.6

## Details
An issue was discovered in Django 3.2 before 3.2.14 and 4.0 before 4.0.6. The `Trunc()` and `Extract()` database functions are subject to SQL injection if untrusted data is used as a kind/lookup_name value. Applications that constrain the lookup name and kind choice to a known safe list are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34265
- https://github.com/django/django/commit/0dc9c016fadb71a067e5a42be30164e3f96c0492
- https://github.com/django/django/commit/5e2f4ddf2940704a26a4ac782b851989668d74db
- https://github.com/django/django/commit/877c800f255ccaa7abde1fb944de45d1616f5cc9
- https://github.com/django/django/commit/a9010fe5555e6086a9d9ae50069579400ef0685e
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/advisories/GHSA-p64x-8rxx-wf6q
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-213.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://security.netapp.com/advisory/ntap-20220818-0006
- https://www.debian.org/security/2022/dsa-5254
- https://www.djangoproject.com/weblog/2022/jul/04/security-releases
