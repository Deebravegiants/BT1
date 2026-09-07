# [M] Django open redirect

## Summary
Severity: Medium
Advisory: GHSA-h4hv-m4h4-mhwg
CVE: CVE-2017-7234
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-h4hv-m4h4-mhwg
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.10 <1.10.7
- PyPI: `Django` — affected >=1.9 <1.9.13
- PyPI: `Django` — affected >=1.8 <1.8.18

## Details
A maliciously crafted URL to a Django (1.10 before 1.10.7, 1.9 before 1.9.13, and 1.8 before 1.8.18) site using the `django.views.static.serve()` view could redirect to any other domain, aka an open redirect vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7234
- https://github.com/django/django/commit/2a9f6ef71b8e23fd267ee2be1be26dde8ab67037
- https://github.com/django/django/commit/4a6b945dffe8d10e7cec107d93e6efaebfbded29
- https://github.com/django/django/commit/5f1ffb07afc1e59729ce2b283124116d6c0659e4
- https://github.com/advisories/GHSA-h4hv-m4h4-mhwg
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2017-10.yaml
- https://web.archive.org/web/20170429023907/http://www.securitytracker.com/id/1038177
- https://web.archive.org/web/20170526042328/http://www.securityfocus.com/bid/97401
- https://www.djangoproject.com/weblog/2017/apr/04/security-releases
- http://www.debian.org/security/2017/dsa-3835
