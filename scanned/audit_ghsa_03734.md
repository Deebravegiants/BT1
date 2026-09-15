# [M] Django denial-of-service possibility in urlize and urlizetrunc template filters

## Summary
Severity: Medium
Advisory: GHSA-r28v-mw67-m5p9
CVE: CVE-2018-7536
CWE: CWE-185
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-r28v-mw67-m5p9
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.0a1 <2.0.3
- PyPI: `Django` — affected >=1.11a1 <1.11.11
- PyPI: `Django` — affected >=1.8a1 <1.8.19

## Details
An issue was discovered in Django 2.0 before 2.0.3, 1.11 before 1.11.11, and 1.8 before 1.8.19. The `django.utils.html.urlize()` function was extremely slow to evaluate certain inputs due to catastrophic backtracking vulnerabilities in two regular expressions (only one regular expression for Django 1.8.x). The `urlize()` function is used to implement the urlize and urlizetrunc template filters, which were thus vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7536
- https://github.com/django/django/commit/1ca63a66ef3163149ad822701273e8a1844192c2
- https://github.com/django/django/commit/abf89d729f210c692a50e0ad3f75fb6bec6fae16
- https://github.com/django/django/commit/e157315da3ae7005fa0683ffc9751dbeca7306c8
- https://access.redhat.com/errata/RHSA-2018:2927
- https://access.redhat.com/errata/RHSA-2019:0051
- https://access.redhat.com/errata/RHSA-2019:0082
- https://access.redhat.com/errata/RHSA-2019:0265
- https://github.com/advisories/GHSA-r28v-mw67-m5p9
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2018-5.yaml
- https://lists.debian.org/debian-lts-announce/2018/03/msg00006.html
- https://usn.ubuntu.com/3591-1
- https://web.archive.org/web/20200227131019/http://www.securityfocus.com/bid/103361
- https://www.debian.org/security/2018/dsa-4161
- https://www.djangoproject.com/weblog/2018/mar/06/security-releases
