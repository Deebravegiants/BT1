# [H] SQL injection in Django

## Summary
Severity: High
Advisory: GHSA-3gh2-xw74-jmcw
CVE: CVE-2020-9402
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-3gh2-xw74-jmcw
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.11 <1.11.29
- PyPI: `Django` — affected >=2.2 <2.2.11
- PyPI: `Django` — affected >=3.0 <3.0.4

## Details
Django 1.11 before 1.11.29, 2.2 before 2.2.11, and 3.0 before 3.0.4 allows SQL Injection if untrusted data is used as a tolerance parameter in GIS functions and aggregates on Oracle. By passing a suitably crafted tolerance to GIS functions and aggregates on Oracle, it was possible to break escaping and inject malicious SQL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9402
- https://github.com/django/django/commit/6695d29b1c1ce979725816295a26ecc64ae0e927
- https://www.djangoproject.com/weblog/2020/mar/04/security-releases
- https://www.debian.org/security/2020/dsa-4705
- https://usn.ubuntu.com/4296-1
- https://security.netapp.com/advisory/ntap-20200327-0004
- https://security.gentoo.org/glsa/202004-17
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UZMN2NKAGTFE3YKMNM2JVJG7R2W7LLHY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4A2AP4T7RKPBCLTI2NNQG3T6MINDUUMZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UZMN2NKAGTFE3YKMNM2JVJG7R2W7LLHY
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4A2AP4T7RKPBCLTI2NNQG3T6MINDUUMZ
- https://lists.debian.org/debian-lts-announce/2022/05/msg00035.html
- https://groups.google.com/forum/#%21topic/django-announce/fLUh_pOaKrY
- https://groups.google.com/forum/#!topic/django-announce/fLUh_pOaKrY
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2020-36.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2020-345.yaml
- https://github.com/django/django
- https://github.com/advisories/GHSA-3gh2-xw74-jmcw
- https://docs.djangoproject.com/en/3.0/releases/security
