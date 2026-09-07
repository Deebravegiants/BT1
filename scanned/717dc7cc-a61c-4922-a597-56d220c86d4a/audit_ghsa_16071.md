# [M] Django Filer Unrestricted Upload of File with Dangerous Type

## Summary
Severity: Medium
Advisory: GHSA-j4v3-wwwx-5gqv
CVE: CVE-2024-11404
CWE: CWE-20, CWE-434, CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-j4v3-wwwx-5gqv
Type: github-advisory

## Affected
- PyPI: `django-filer` — affected >=0 <3.3.0

## Details
Unrestricted Upload of File with Dangerous Type, Improper Input Validation, Improper Neutralization of Script-Related HTML Tags in a Web Page (Basic XSS) vulnerability in django CMS Association django Filer allows Input Data Manipulation, Stored XSS.This issue affects django Filer: from 3 before 3.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11404
- https://github.com/django-cms/django-filer/commit/f8209a6507680661bd134cd30878993b79ef3344
- https://github.com/django-cms/django-filer
- https://iltosec.com/blog/post/cve-2024-11404-medium-severity-file-upload-vulnerabilities-in-django-filer-323
- https://iltosec.com/blog/post/djangocms-attributes-field-300-stored-xss-vulnerability
- https://pypi.org/project/django-filer
- https://siberguvenlik.gov.tr/guvenlik-bildirimleri/detay/tr-24-1864
- https://www.django-cms.org/en/blog/2024/11/19/security-updates-for-django-filer-and-django-cms-attributes-field
- https://www.usom.gov.tr/bildirim/tr-24-1864
