# [H] Django Denial of Service Vulnerability in the authentication framework 

## Summary
Severity: High
Advisory: GHSA-4c42-4rxm-x6qf
CVE: CVE-2013-1443
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4c42-4rxm-x6qf
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.4 <1.4.8
- PyPI: `Django` — affected >=1.5 <1.5.4

## Details
The authentication framework (django.contrib.auth) in Django 1.4.x before 1.4.8, 1.5.x before 1.5.4, and 1.6.x before 1.6 beta 4 allows remote attackers to cause a denial of service (CPU consumption) via a long password which is then hashed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1443
- https://github.com/django/django/commit/22b74fa09d7ccbc8c52270d648a0da7f3f0fa2bc
- https://github.com/django/django/commit/3f3d887a6844ec2db743fee64c9e53e04d39a368
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2013-18.yaml
- https://www.djangoproject.com/weblog/2013/sep/15/security
- http://lists.opensuse.org/opensuse-updates/2013-10/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2013-11/msg00035.html
- http://python.6.x6.nabble.com/Set-a-reasonable-upper-bound-on-password-length-td5032218.html
- http://www.debian.org/security/2013/dsa-2758
