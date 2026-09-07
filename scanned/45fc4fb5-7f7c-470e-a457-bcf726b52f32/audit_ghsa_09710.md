# [H] Django vulnerable to ASGI header spoofing via underscore/hyphen conflation

## Summary
Severity: High
Advisory: GHSA-mvfq-ggxm-9mc5
CVE: CVE-2026-3902
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-mvfq-ggxm-9mc5
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=6.0 <6.0.4
- PyPI: `Django` — affected >=5.2 <5.2.13
- PyPI: `Django` — affected >=4.2 <4.2.30

## Details
An issue was discovered in 6.0 before 6.0.4, 5.2 before 5.2.13, and 4.2 before 4.2.30. `ASGIRequest` allows a remote attacker to spoof headers by exploiting an ambiguous mapping of two header variants (with hyphens or with underscores) to a single version with underscores.

Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Tarek Nakkouch for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3902
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2026-51.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2026/apr/07/security-releases
