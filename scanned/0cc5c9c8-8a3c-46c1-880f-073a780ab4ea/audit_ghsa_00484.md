# [M] Django allows unprivileged users to read the password hashes of arbitrary accounts

## Summary
Severity: Medium
Advisory: GHSA-6mx3-3vqg-hpp2
CVE: CVE-2018-16984
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-03
Source: https://github.com/advisories/GHSA-6mx3-3vqg-hpp2
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.1 <2.1.2

## Details
An issue was discovered in Django 2.1 before 2.1.2, in which unprivileged users can read the password hashes of arbitrary accounts. The read-only password widget used by the Django Admin to display an obfuscated password hash was bypassed if a user has only the "view" permission (new in Django 2.1), resulting in display of the entire password hash to those users. This may result in a vulnerability for sites with legacy user accounts using insecure hashes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16984
- https://github.com/django/django/commit/bf39978a53f117ca02e9a0c78b76664a41a54745
- https://github.com/advisories/GHSA-6mx3-3vqg-hpp2
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2018-3.yaml
- https://security.netapp.com/advisory/ntap-20190502-0009
- https://web.archive.org/web/20200517123022/http://www.securitytracker.com/id/1041749
- https://www.djangoproject.com/weblog/2018/oct/01/security-release
