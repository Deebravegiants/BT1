# [H] Django Reuses Cached CSRF Token

## Summary
Severity: High
Advisory: GHSA-89hj-xfx5-7q66
CVE: CVE-2014-0473
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-89hj-xfx5-7q66
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.11
- PyPI: `Django` — affected >=1.5 <1.5.6
- PyPI: `Django` — affected >=1.6 <1.6.3

## Details
The caching framework in Django before 1.4.11, 1.5.x before 1.5.6, 1.6.x before 1.6.3, and 1.7.x before 1.7 beta 2 reuses a cached CSRF token for all anonymous users, which allows remote attackers to bypass CSRF protections by reading the CSRF cookie for anonymous users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0473
- https://github.com/django/django/commit/1170f285ddd6a94a65f911a27788ba49ca08c0b0
- https://github.com/django/django/commit/6872f42757d7ef6a97e0b6ec5db4d2615d8a2bd8
- https://github.com/django/django/commit/d63e20942f3024f24cb8cd85a49461ba8a9b6736
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2014-2.yaml
- https://www.djangoproject.com/weblog/2014/apr/21/security
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00023.html
- http://rhn.redhat.com/errata/RHSA-2014-0456.html
- http://rhn.redhat.com/errata/RHSA-2014-0457.html
- http://www.debian.org/security/2014/dsa-2934
- http://www.ubuntu.com/usn/USN-2169-1
