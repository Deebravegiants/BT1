# [H] Resource exhaustion in Django

## Summary
Severity: High
Advisory: GHSA-2hrw-hx67-34x6
CVE: CVE-2023-24580
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-2hrw-hx67-34x6
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2a1 <3.2.18
- PyPI: `Django` — affected >=4.1a1 <4.1.7
- PyPI: `Django` — affected >=4.0a1 <4.0.10

## Details
An issue was discovered in the Multipart Request Parser in Django 3.2 before 3.2.18, 4.0 before 4.0.10, and 4.1 before 4.1.7. Passing certain inputs (e.g., an excessive number of parts) to multipart forms could result in too many open files or memory exhaustion, and provided a potential vector for a denial-of-service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24580
- https://github.com/django/django/commit/628b33a854a9c68ec8a0c51f382f304a0044ec92
- https://github.com/django/django/commit/83f1ea83e4553e211c1c5a0dfc197b66d4e50432
- https://github.com/django/django/commit/a665ed5179f5bbd3db95ce67286d0192eff041d8
- https://www.djangoproject.com/weblog/2023/feb/14/security-releases
- https://security.netapp.com/advisory/ntap-20230316-0006
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YJB6FUBBLVKKG655UMTLQNN6UQ6EDLSP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VZS4G6NSZWPTVXMMZHJOJVQEPL3QTO77
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FKYVMMR7RPM6AHJ2SBVM2LO6D3NGFY7B
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YJB6FUBBLVKKG655UMTLQNN6UQ6EDLSP
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZS4G6NSZWPTVXMMZHJOJVQEPL3QTO77
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FKYVMMR7RPM6AHJ2SBVM2LO6D3NGFY7B
- https://lists.debian.org/debian-lts-announce/2023/02/msg00023.html
- https://groups.google.com/forum/#%21forum/django-announce
- https://groups.google.com/forum/#!forum/django-announce
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2023-13.yaml
