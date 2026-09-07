# [M] Django is vulnerable to SQL injection in column aliases

## Summary
Severity: Medium
Advisory: GHSA-rqw2-ghq9-44m7
CVE: CVE-2025-13372
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-rqw2-ghq9-44m7
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.2a1 <5.2.9
- PyPI: `Django` — affected >=5.1a1 <5.1.15
- PyPI: `Django` — affected >=4.2a1 <4.2.27

## Details
An issue was discovered in 5.2 before 5.2.9, 5.1 before 5.1.15, and 4.2 before 4.2.27.
`FilteredRelation` is subject to SQL injection in column aliases, using a suitably crafted dictionary, with dictionary expansion, as the `**kwargs` passed to `QuerySet.annotate()` or `QuerySet.alias()` on PostgreSQL.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Stackered for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13372
- https://github.com/django/django/commit/479415ce5249bcdebeb6570c72df2a87f45a7bbf
- https://github.com/django/django/commit/56aea00c3c5e1aacf4ed05f8ee06c2e78f02cea0
- https://github.com/django/django/commit/5b90ca1e7591fa36fccf2d6dad67cf1477e6293e
- https://github.com/django/django/commit/9c6a5bde24240382807d13bc3748d08444709355
- https://github.com/django/django/commit/f997037b235f6b5c9e7c4a501491ec45f3400f3d
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2025-104.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2025/dec/02/security-releases
