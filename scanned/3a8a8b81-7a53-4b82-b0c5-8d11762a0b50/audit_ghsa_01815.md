# [M] Potential bypass of an upstream access control based on URL paths in Django

## Summary
Severity: Medium
Advisory: GHSA-v6rh-hp5x-86rv
CVE: CVE-2021-44420
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-v6rh-hp5x-86rv
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2a1 <2.2.25
- PyPI: `Django` — affected >=3.0a1 <3.1.14
- PyPI: `Django` — affected >=3.2a1 <3.2.10

## Details
In Django 2.2 before 2.2.25, 3.1 before 3.1.14, and 3.2 before 3.2.10, HTTP requests for URLs with trailing newlines could bypass upstream access control based on URL paths. This issue has low severity, according to the Django security policy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44420
- https://github.com/django/django/commit/d4dcd5b9dd9e462fec8220e33e3e6c822b7e88a6
- https://docs.djangoproject.com/en/3.2/releases/security
- https://github.com/advisories/GHSA-v6rh-hp5x-86rv
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-439.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://security.netapp.com/advisory/ntap-20211229-0006
- https://www.djangoproject.com/weblog/2021/dec/07/security-releases
- https://www.openwall.com/lists/oss-security/2021/12/07/1
