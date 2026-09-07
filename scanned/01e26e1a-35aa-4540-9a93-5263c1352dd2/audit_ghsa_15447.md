# [C] Django SQL injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-pv4p-cwwg-4rph
CVE: CVE-2024-42005
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-07
Source: https://github.com/advisories/GHSA-pv4p-cwwg-4rph
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.0 <5.0.8
- PyPI: `Django` — affected >=4.2 <4.2.15

## Details
An issue was discovered in Django 5.0 before 5.0.8 and 4.2 before 4.2.15. QuerySet.values() and values_list() methods on models with a JSONField are subject to SQL injection in column aliases via a crafted JSON object key as a passed *arg.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42005
- https://github.com/django/django/commit/32ebcbf2e1fe3e5ba79a6554a167efce81f7422d
- https://github.com/django/django/commit/f4af67b9b41e0f4c117a8741da3abbd1c869ab28
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-70.yaml
- https://groups.google.com/forum/#%21forum/django-announce
- https://security.netapp.com/advisory/ntap-20240905-0007
- https://www.djangoproject.com/weblog/2024/aug/06/security-releases
