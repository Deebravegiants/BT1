# [M] Django open redirect

## Summary
Severity: Medium
Advisory: GHSA-5hg3-6c2f-f3wr
CVE: CVE-2018-14574
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-04
Source: https://github.com/advisories/GHSA-5hg3-6c2f-f3wr
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.0 <2.0.8
- PyPI: `Django` — affected >=1.11 <1.11.15

## Details
`django.middleware.common.CommonMiddleware` in Django 1.11.x before 1.11.15 and 2.0.x before 2.0.8 has an Open Redirect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14574
- https://github.com/django/django/commit/6fffc3c6d420e44f4029d5643f38d00a39b08525
- https://github.com/django/django/commit/c4e5ff7fdb5fce447675e90291fd33fddd052b3c
- https://github.com/django/django/commit/d6eaee092709aad477a9894598496c6deec532ff
- https://access.redhat.com/errata/RHSA-2019:0265
- https://github.com/advisories/GHSA-5hg3-6c2f-f3wr
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2018-2.yaml
- https://usn.ubuntu.com/3726-1
- https://web.archive.org/web/20190901075632/http://www.securitytracker.com/id/1041403
- https://web.archive.org/web/20200227115315/http://www.securityfocus.com/bid/104970
- https://www.debian.org/security/2018/dsa-4264
- https://www.djangoproject.com/weblog/2018/aug/01/security-releases
