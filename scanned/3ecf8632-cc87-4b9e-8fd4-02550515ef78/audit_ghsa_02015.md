# [H] Path Traversal in Django

## Summary
Severity: High
Advisory: GHSA-rxjp-mfm9-w4wr
CVE: CVE-2021-31542
CWE: CWE-22, CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-04
Source: https://github.com/advisories/GHSA-rxjp-mfm9-w4wr
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.21
- PyPI: `Django` — affected >=3.0 <3.1.9
- PyPI: `Django` — affected >=3.2 <3.2.1

## Details
In Django 2.2 before 2.2.21, 3.1 before 3.1.9, and 3.2 before 3.2.1, MultiPartParser, UploadedFile, and FieldFile allowed directory traversal via uploaded files with suitably crafted file names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31542
- https://github.com/django/django/commit/04ac1624bdc2fa737188401757cf95ced122d26d
- https://github.com/django/django/commit/25d84d64122c15050a0ee739e859f22ddab5ac48
- https://github.com/django/django/commit/c98f446c188596d4ba6de71d1b77b4a6c5c2a007
- https://www.djangoproject.com/weblog/2021/may/04/security-releases
- https://security.netapp.com/advisory/ntap-20210618-0001
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZVKYPHR3TKR2ESWXBPOJEKRO2OSJRZUE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZVKYPHR3TKR2ESWXBPOJEKRO2OSJRZUE
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://lists.debian.org/debian-lts-announce/2021/05/msg00005.html
- https://groups.google.com/forum/#%21forum/django-announce
- https://groups.google.com/forum/#!forum/django-announce
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-7.yaml
- https://github.com/django/django
- https://github.com/advisories/GHSA-rxjp-mfm9-w4wr
- https://docs.djangoproject.com/en/3.2/releases/security
- http://www.openwall.com/lists/oss-security/2021/05/04/3
