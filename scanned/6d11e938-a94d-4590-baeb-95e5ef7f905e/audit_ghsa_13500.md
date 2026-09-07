# [M] Django Grappelli Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9x43-5qcq-h79q
CVE: CVE-2021-46898
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-22
Source: https://github.com/advisories/GHSA-9x43-5qcq-h79q
Type: github-advisory

## Affected
- PyPI: `django-grappelli` — affected >=0 <2.15.2

## Details
views/switch.py in django-grappelli (aka Django Grappelli) before 2.15.2 attempts to prevent external redirection with startswith("/") but this does not consider a protocol-relative URL (e.g., //example.com) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46898
- https://github.com/sehmaschine/django-grappelli/issues/975
- https://github.com/sehmaschine/django-grappelli/pull/976
- https://github.com/sehmaschine/django-grappelli/commit/4ca94bcda0fa2720594506853d85e00c8212968f
- https://github.com/pypa/advisory-database/tree/main/vulns/django-grappelli/PYSEC-2023-211.yaml
- https://github.com/sehmaschine/django-grappelli
- https://github.com/sehmaschine/django-grappelli/compare/2.15.1...2.15.2
