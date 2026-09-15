# [H] Django denial-of-service vulnerability in internationalized URLs

## Summary
Severity: High
Advisory: GHSA-qrw5-5h28-6cmg
CVE: CVE-2022-41323
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-16
Source: https://github.com/advisories/GHSA-qrw5-5h28-6cmg
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2 <3.2.16
- PyPI: `Django` — affected >=4.0 <4.0.8
- PyPI: `Django` — affected >=4.1 <4.1.2

## Details
In Django 3.2 before 3.2.16, 4.0 before 4.0.8, and 4.1 before 4.1.2, internationalized URLs were subject to a potential denial of service attack via the locale parameter, which is treated as a regular expression.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41323
- https://github.com/django/django/commit/23f0093125ac2e553da6c1b2f9988eb6a3dd2ea1
- https://github.com/django/django/commit/5b6b257fa7ec37ff27965358800c67e2dd11c924
- https://github.com/django/django/commit/9d656ea51d9ea7105c0c0785783ac29d426a7d25
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-304.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FKYVMMR7RPM6AHJ2SBVM2LO6D3NGFY7B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VZS4G6NSZWPTVXMMZHJOJVQEPL3QTO77
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YJB6FUBBLVKKG655UMTLQNN6UQ6EDLSP
- https://security.netapp.com/advisory/ntap-20221124-0001
- https://www.djangoproject.com/weblog/2022/oct/04/security-releases
