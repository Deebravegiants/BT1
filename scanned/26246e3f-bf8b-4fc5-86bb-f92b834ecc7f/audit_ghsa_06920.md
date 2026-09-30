# [M] Django: DomainNameValidator permits newline characters that may enable HTTP header injection

## Summary
Severity: Medium
Advisory: GHSA-8qcx-xf44-272x
CVE: CVE-2026-53878
CWE: CWE-144
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-8qcx-xf44-272x
Type: github-advisory

## Affected
- PyPI: `django` — affected >=0 <5.2.16
- PyPI: `django` — affected >=6.0.0 <6.0.7

## Details
An issue was discovered in Django 6.0 before 6.0.7 and 5.2 before 5.2.16.
`DomainNameValidator` does not prohibit newlines in domain names (unless used via a form field, since `CharField` strips newlines). If an application uses values with newlines in an HTTP response, header injection can occur. Django itself is unaffected because `HttpResponse` prohibits newlines in HTTP headers.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Bence Nagy for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53878
- https://github.com/django/django/commit/3a720d0d8bf2529253b98968f10ca73daf6d693c
- https://github.com/django/django/commit/a5de13f1491f1dbf2bb0ad9b91570524ebbc8acd
- https://github.com/django/django/commit/d5d60ed0323cddaa0ce0237a26a3d49ac21ee05e
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2026-2092.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2026/jul/07/security-releases
