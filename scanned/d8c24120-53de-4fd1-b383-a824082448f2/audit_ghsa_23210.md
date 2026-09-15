# [H] Django Directory Traversal via ssi template tag

## Summary
Severity: High
Advisory: GHSA-vjjp-9r83-22rc
CVE: CVE-2013-4315
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vjjp-9r83-22rc
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.4 <1.4.7
- PyPI: `Django` — affected >=1.5 <1.5.3

## Details
Directory traversal vulnerability in Django 1.4.x before 1.4.7, 1.5.x before 1.5.3, and 1.6.x before 1.6 beta 3 allows remote attackers to read arbitrary files via a file path in the ALLOWED_INCLUDE_ROOTS setting followed by a `..` (dot dot) in a ssi template tag.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4315
- https://github.com/django/django/commit/87d2750b39f6f2d54b7047225521a44dcd37e896
- https://github.com/django/django/commit/988b61c550d798f9a66d17ee0511fb7a9a7f33ca
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2013-20.yaml
- https://www.djangoproject.com/weblog/2013/sep/10/security-releases-issued
- http://lists.opensuse.org/opensuse-updates/2013-10/msg00015.html
- http://rhn.redhat.com/errata/RHSA-2013-1521.html
- http://www.debian.org/security/2013/dsa-2755
