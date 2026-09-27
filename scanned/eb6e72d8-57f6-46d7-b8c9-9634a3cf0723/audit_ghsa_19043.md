# [C] Django vulnerable to SQL injection via _connector keyword argument in QuerySet and Q objects.

## Summary
Severity: Critical
Advisory: GHSA-frmv-pr5f-9mcr
CVE: CVE-2025-64459
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-05
Source: https://github.com/advisories/GHSA-frmv-pr5f-9mcr
Type: github-advisory

## Affected
- PyPI: `django` — affected >=5.2a1 <5.2.8
- PyPI: `django` — affected >=5.0a1 <5.1.14
- PyPI: `django` — affected >=0 <4.2.26

## Details
An issue was discovered in 5.1 before 5.1.14, 4.2 before 4.2.26, and 5.2 before 5.2.8.
The methods `QuerySet.filter()`, `QuerySet.exclude()`, and `QuerySet.get()`, and the class `Q()`, are subject to SQL injection when using a suitably crafted dictionary, with dictionary expansion, as the `_connector` argument.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank cyberstan for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64459
- https://github.com/django/django/commit/06dd38324ac3d60d83d9f3adabf0dcdf423d2a85
- https://github.com/django/django/commit/59ae82e67053d281ff4562a24bbba21299f0a7d4
- https://github.com/django/django/commit/6703f364d767e949c5b0e4016433ef75063b4f9b
- https://github.com/django/django/commit/72d2c87431f2ae0431d65d0ec792047f078c8241
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/omarkurt/django-connector-CVE-2025-64459-testbed
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2025-108.yaml
- https://groups.google.com/g/django-announce
- https://shivasurya.me/security/django/2025/11/07/django-sql-injection-CVE-2025-64459.html
- https://www.djangoproject.com/weblog/2025/nov/05/security-releases
