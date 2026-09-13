# [M] Django allows enumeration of user e-mail addresses

## Summary
Severity: Medium
Advisory: GHSA-rrqc-c2jx-6jgv
CVE: CVE-2024-45231
CWE: CWE-203, CWE-204
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-rrqc-c2jx-6jgv
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.1 <5.1.1
- PyPI: `Django` — affected >=5.0 <5.0.9
- PyPI: `Django` — affected >=0 <4.2.16

## Details
An issue was discovered in Django v5.1.1, v5.0.9, and v4.2.16. The django.contrib.auth.forms.PasswordResetForm class, when used in a view implementing password reset flows, allows remote attackers to enumerate user e-mail addresses by sending password reset requests and observing the outcome (only when e-mail sending is consistently failing).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45231
- https://github.com/django/django/commit/3c733c78d6f8e50296d6e248968b6516c92a53ca
- https://github.com/django/django/commit/96d84047715ea1715b4bd1594e46122b8a77b9e2
- https://github.com/django/django/commit/bf4888d317ba4506d091eeac6e8b4f1fcc731199
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://groups.google.com/forum/#%21forum/django-announce
- https://www.djangoproject.com/weblog/2024/sep/03/security-releases
