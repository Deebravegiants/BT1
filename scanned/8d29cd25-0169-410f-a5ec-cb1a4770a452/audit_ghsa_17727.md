# [M] Django has a potential denial-of-service vulnerability in IPv6 validation

## Summary
Severity: Medium
Advisory: GHSA-qcgg-j2x8-h9g8
CVE: CVE-2024-56374
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-qcgg-j2x8-h9g8
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.1 <5.1.5
- PyPI: `Django` — affected >=5.0 <5.0.11
- PyPI: `Django` — affected >=4.2 <4.2.18
- PyPI: `django` — affected >=5.1 <5.1.5
- PyPI: `django` — affected >=5.0 <5.0.11
- PyPI: `django` — affected >=4.2 <4.2.18

## Details
An issue was discovered in Django 5.1 before 5.1.5, 5.0 before 5.0.11, and 4.2 before 4.2.18. Lack of upper-bound limit enforcement in strings passed when performing IPv6 validation could lead to a potential denial-of-service attack. The undocumented and private functions `clean_ipv6_address` and `is_valid_ipv6_address` are vulnerable, as is the `django.forms.GenericIPAddressField` form field. (The django.db.models.GenericIPAddressField model field is not affected.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56374
- https://github.com/django/django/commit/4806731e58f3e8700a3c802e77899d54ac6021fe
- https://github.com/django/django/commit/ad866a1ca3e7d60da888d25d27e46a8adb2ed36e
- https://github.com/django/django/commit/ca2be7724e1244a4cb723de40a070f873c6e94bf
- https://github.com/django/django/commit/e8d4a2005955dcf962193600b53bf461b190b455
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2025-1.yaml
- https://groups.google.com/g/django-announce
- https://lists.debian.org/debian-lts-announce/2025/01/msg00024.html
- https://www.djangoproject.com/weblog/2025/jan/14/security-releases
- http://www.openwall.com/lists/oss-security/2025/01/14/2
