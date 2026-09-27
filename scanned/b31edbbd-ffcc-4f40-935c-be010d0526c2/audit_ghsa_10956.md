# [H] Django vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-8p8v-wh79-9r56
CVE: CVE-2026-25673
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-8p8v-wh79-9r56
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=6.0 <6.0.3
- PyPI: `Django` — affected >=5.2 <5.2.12
- PyPI: `Django` — affected >=4.2 <4.2.29

## Details
An issue was discovered in 6.0 before 6.0.3, 5.2 before 5.2.12, and 4.2 before 4.2.29.

`URLField.to_python()` in Django calls `urllib.parse.urlsplit()`, which performs NFKC normalization on Windows that is disproportionately slow for certain Unicode characters, allowing a remote attacker to cause denial of service via large URL inputs containing these characters.

Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Seokchan Yoon for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25673
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2026/mar/03/security-releases
