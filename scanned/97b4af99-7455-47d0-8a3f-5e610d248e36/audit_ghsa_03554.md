# [H] Django Incorrect Default Permissions

## Summary
Severity: High
Advisory: GHSA-m6gj-h9gm-gw44
CVE: CVE-2020-24583
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-03-18
Source: https://github.com/advisories/GHSA-m6gj-h9gm-gw44
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2a1 <2.2.16
- PyPI: `Django` — affected >=3.0a1 <3.0.10
- PyPI: `Django` — affected >=3.1a1 <3.1.1

## Details
An issue was discovered in Django 2.2 before 2.2.16, 3.0 before 3.0.10, and 3.1 before 3.1.1 (when Python 3.7+ is used). FILE_UPLOAD_DIRECTORY_PERMISSIONS mode was not applied to intermediate-level directories created in the process of uploading files. It was also not applied to intermediate-level collected static directories when using the collectstatic management command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24583
- https://github.com/django/django/commit/8d7271578d7b153435b40fe40236ebec43cbf1b9
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/advisories/GHSA-m6gj-h9gm-gw44
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2020-33.yaml
- https://groups.google.com/forum/#!topic/django-announce/Gdqn58RqIDM
- https://groups.google.com/forum/#!topic/django-announce/zFCMdgUnutU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/F2ZHO3GZCJMP3DDTXCNVFV6ED3W64NAU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OLGFFLMF3X6USMJD7V5F5P4K2WVUTO3T
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZCRPQCBTV3RZHKVZ6K6QOAANPRZQD3GI
- https://security.netapp.com/advisory/ntap-20200918-0004
- https://usn.ubuntu.com/4479-1
- https://www.djangoproject.com/weblog/2020/sep/01/security-releases
- https://www.openwall.com/lists/oss-security/2020/09/01/2
- https://www.oracle.com/security-alerts/cpujan2021.html
