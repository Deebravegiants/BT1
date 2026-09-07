# [M] Directory-traversal in Django

## Summary
Severity: Medium
Advisory: GHSA-jrh2-hc4r-7jwx
CVE: CVE-2021-45452
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-jrh2-hc4r-7jwx
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.26
- PyPI: `Django` — affected >=3.2 <3.2.11
- PyPI: `Django` — affected >=4.0 <4.0.1

## Details
Storage.save in Django 2.2 before 2.2.26, 3.2 before 3.2.11, and 4.0 before 4.0.1 allows directory traversal if crafted filenames are directly passed to it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45452
- https://github.com/django/django/commit/4cb35b384ceef52123fc66411a73c36a706825e1
- https://github.com/django/django/commit/8d2f7cff76200cbd2337b2cf1707e383eb1fb54b
- https://github.com/django/django/commit/e1592e0f26302e79856cc7f2218ae848ae19b0f6
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/advisories/GHSA-jrh2-hc4r-7jwx
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-3.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://security.netapp.com/advisory/ntap-20220121-0005
- https://www.djangoproject.com/weblog/2022/jan/04/security-releases
