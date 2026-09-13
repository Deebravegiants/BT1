# [M] Path Traversal in Django

## Summary
Severity: Medium
Advisory: GHSA-68w8-qjq3-2gfm
CVE: CVE-2021-33203
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-10
Source: https://github.com/advisories/GHSA-68w8-qjq3-2gfm
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <2.2.24
- PyPI: `Django` — affected >=3.0 <3.1.12
- PyPI: `Django` — affected >=3.2 <3.2.4

## Details
Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33203
- https://github.com/django/django/commit/053cc9534d174dc89daba36724ed2dcb36755b90
- https://github.com/django/django/commit/20c67a0693c4ede2b09af02574823485e82e4c8f
- https://github.com/django/django/commit/dfaba12cda060b8b292ae1d271b44bf810b1c5b9
- https://docs.djangoproject.com/en/3.2/releases/security
- https://github.com/advisories/GHSA-68w8-qjq3-2gfm
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-98.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://security.netapp.com/advisory/ntap-20210727-0004
- https://www.djangoproject.com/weblog/2021/jun/02/security-releases
