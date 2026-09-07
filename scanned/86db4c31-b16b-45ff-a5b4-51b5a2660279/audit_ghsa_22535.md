# [M] Django allows user sessions hijacking via an empty string in the session key

## Summary
Severity: Medium
Advisory: GHSA-6wgp-fwfm-mxp3
CVE: CVE-2015-3982
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6wgp-fwfm-mxp3
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.8a1 <1.8.2

## Details
The session.flush function in the cached_db backend in Django 1.8.x before 1.8.2 does not properly flush the session, which allows remote attackers to hijack user sessions via an empty string in the session key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3982
- https://github.com/django/django/commit/31cb25adecba930bdeee4556709f5a1c42d88fd6
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-19.yaml
- https://web.archive.org/web/20200228092138/http://www.securityfocus.com/bid/74960
- https://www.djangoproject.com/weblog/2015/may/20/security-release
