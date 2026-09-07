# [H] Django has an SQL Injection issue

## Summary
Severity: High
Advisory: GHSA-gvg8-93h5-g6qq
CVE: CVE-2026-1287
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-gvg8-93h5-g6qq
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=6.0a1 <6.0.2
- PyPI: `Django` — affected >=5.2a1 <5.2.11
- PyPI: `Django` — affected >=4.2a1 <4.2.28

## Details
An issue was discovered in 6.0 before 6.0.2, 5.2 before 5.2.11, and 4.2 before 4.2.28.

`FilteredRelation` is subject to SQL injection in column aliases via control characters, using a suitably crafted dictionary, with dictionary expansion, as the `**kwargs` passed to `QuerySet` methods `annotate()`, `aggregate()`, `extra()`, `values()`, `values_list()`, and `alias()`. Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.

Django would like to thank Solomon Kebede for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1287
- https://github.com/django/django/commit/e891a84c7ef9962bfcc3b4685690219542f86a22
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2026-46.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2026/feb/03/security-releases
