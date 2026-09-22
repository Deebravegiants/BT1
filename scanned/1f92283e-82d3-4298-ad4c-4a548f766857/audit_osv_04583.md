# [H] BIT-django-2020-24584

## Summary
Severity: High
Advisory: BIT-django-2020-24584
Aliases: CVE-2020-24584, GHSA-fr28-569j-53c4, PYSEC-2020-34
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-django-2020-24584
Type: osv

## Affected
- Bitnami: `django` — affected >=3.1.0 <3.1.1

## Details
An issue was discovered in Django 2.2 before 2.2.16, 3.0 before 3.0.10, and 3.1 before 3.1.1 (when Python 3.7+ is used). The intermediate-level directories of the filesystem cache had the system's standard umask rather than 0o077.

## References
- https://docs.djangoproject.com/en/dev/releases/security/
- https://groups.google.com/forum/#%21topic/django-announce/Gdqn58RqIDM
- https://groups.google.com/forum/#%21topic/django-announce/zFCMdgUnutU
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F2ZHO3GZCJMP3DDTXCNVFV6ED3W64NAU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OLGFFLMF3X6USMJD7V5F5P4K2WVUTO3T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZCRPQCBTV3RZHKVZ6K6QOAANPRZQD3GI/
- https://security.netapp.com/advisory/ntap-20200918-0004/
- https://usn.ubuntu.com/4479-1/
- https://www.djangoproject.com/weblog/2020/sep/01/security-releases/
- https://www.openwall.com/lists/oss-security/2020/09/01/2
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-24584
