# [M] Django has potential DoS via MultiPartParser through crafted multipart uploads

## Summary
Severity: Medium
Advisory: GHSA-5mf9-h53q-7mhq
CVE: CVE-2026-33033
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-5mf9-h53q-7mhq
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=6.0 <6.0.4
- PyPI: `Django` — affected >=5.2 <5.2.13
- PyPI: `Django` — affected >=4.2 <4.2.30

## Details
An issue was discovered in 6.0 before 6.0.4, 5.2 before 5.2.13, and 4.2 before 4.2.30. `MultiPartParser` allows remote attackers to degrade performance by submitting multipart uploads with `Content-Transfer-Encoding: base64` including excessive whitespace.

Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Seokchan Yoon for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33033
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2026-48.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2026/apr/07/security-releases
