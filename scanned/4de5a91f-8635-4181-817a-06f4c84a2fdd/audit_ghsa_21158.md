# [M] Django REST framework XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xqcf-hj92-967m
CVE: CVE-2018-25045
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-24
Source: https://github.com/advisories/GHSA-xqcf-hj92-967m
Type: github-advisory

## Affected
- PyPI: `django-rest-framework` — affected >=0 <3.9.1

## Details
Django REST framework (aka django-rest-framework) before 3.9.1 allows XSS because the default DRF Browsable API view templates disable autoescaping.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25045
- https://github.com/encode/django-rest-framework/pull/6191
- https://github.com/encode/django-rest-framework/pull/6330
- https://github.com/encode/django-rest-framework/commit/4bb9a3c48427867ef1e46f7dee945a4c25a4f9b8
- https://github.com/encode/django-rest-framework
