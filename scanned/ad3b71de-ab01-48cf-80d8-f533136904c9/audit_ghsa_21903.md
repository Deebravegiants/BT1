# [H] Infinite Loop in Django

## Summary
Severity: High
Advisory: GHSA-6cw3-g6wv-c2xv
CVE: CVE-2022-23833
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-04
Source: https://github.com/advisories/GHSA-6cw3-g6wv-c2xv
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.27
- PyPI: `Django` — affected >=3.2 <3.2.12
- PyPI: `Django` — affected >=4.0 <4.0.2

## Details
An issue was discovered in MultiPartParser in Django 2.2 before 2.2.27, 3.2 before 3.2.12, and 4.0 before 4.0.2. Passing certain inputs to multipart forms could result in an infinite loop when parsing files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23833
- https://github.com/django/django/commit/c477b761804984c932704554ad35f78a2e230c6a
- https://github.com/django/django/commit/d16133568ef9c9b42cb7a08bdf9ff3feec2e5468
- https://github.com/django/django/commit/f9c7d48fdd6f198a6494a9202f90242f176e4fc9
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/advisories/GHSA-6cw3-g6wv-c2xv
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-20.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://security.netapp.com/advisory/ntap-20220221-0003
- https://www.debian.org/security/2022/dsa-5254
- https://www.djangoproject.com/weblog/2022/feb/01/security-releases
