# [M] Django Data leakage via admin history log

## Summary
Severity: Medium
Advisory: GHSA-r7w6-p47g-vj53
CVE: CVE-2013-0305
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-r7w6-p47g-vj53
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.3 <1.3.6
- PyPI: `Django` — affected >=1.4 <1.4.4

## Details
The administrative interface for Django 1.3.x before 1.3.6, 1.4.x before 1.4.4, and 1.5 before release candidate 2 does not check permissions for the history view, which allows remote authenticated administrators to obtain sensitive object history information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0305
- https://github.com/django/django/commit/0e7861aec73702f7933ce2a93056f7983939f0d6
- https://github.com/django/django/commit/d3a45e10c8ac8268899999129daa27652ec0da35
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2013-16.yaml
- https://www.djangoproject.com/weblog/2013/feb/19/security
- http://rhn.redhat.com/errata/RHSA-2013-0670.html
- http://ubuntu.com/usn/usn-1757-1
- http://www.debian.org/security/2013/dsa-2634
