# [H] django-cms CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-2pqc-gv8q-pvqv
CVE: CVE-2015-5081
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2pqc-gv8q-pvqv
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=0 <3.0.14
- PyPI: `django-cms` — affected >=3.1.0b1 <3.1.1

## Details
Cross-site request forgery (CSRF) vulnerability in django CMS before 3.0.14, 3.1.x before 3.1.1 allows remote attackers to manipulate privileged users into performing unknown actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5081
- https://github.com/divio/django-cms/commit/f77cbc607d6e2a62e63287d37ad320109a2cc78a
- https://github.com/django-cms/django-cms/commit/f77cbc607d6e2a62e63287d37ad320109a2cc78a
- https://github.com/pypa/advisory-database/tree/main/vulns/django-cms/PYSEC-2017-11.yaml
- https://www.django-cms.org/en/blog/2015/06/27/311-3014-release
- http://www.openwall.com/lists/oss-security/2015/06/28/1
