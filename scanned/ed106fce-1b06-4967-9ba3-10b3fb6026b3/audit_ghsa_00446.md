# [H] Django vulnerable to information leakage in AuthenticationForm

## Summary
Severity: High
Advisory: GHSA-rf4j-j272-fj86
CVE: CVE-2018-6188
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-03
Source: https://github.com/advisories/GHSA-rf4j-j272-fj86
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.0a1 <2.0.2
- PyPI: `Django` — affected >=1.11.8 <1.11.10

## Details
`django.contrib.auth.forms.AuthenticationForm` in Django 2.0 before 2.0.2, and 1.11.8 and 1.11.9, allows remote attackers to obtain potentially sensitive information by leveraging data exposure from the `confirm_login_allowed()` method, as demonstrated by discovering whether a user account is inactive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6188
- https://github.com/django/django/commit/57b95fedad5e0b83fc9c81466b7d1751c6427aae
- https://github.com/django/django/commit/c37bb28677295f6edda61d8ac461014ef0d3aeb2
- https://github.com/advisories/GHSA-rf4j-j272-fj86
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2018-4.yaml
- https://usn.ubuntu.com/3559-1
- https://web.archive.org/web/20200517143909/http://www.securitytracker.com/id/1040422
- https://www.djangoproject.com/weblog/2018/feb/01/security-releases
