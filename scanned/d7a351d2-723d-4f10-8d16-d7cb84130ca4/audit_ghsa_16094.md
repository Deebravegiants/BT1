# [M] django CMS Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-gv5h-5655-h4mv
CVE: CVE-2024-11319
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-gv5h-5655-h4mv
Type: github-advisory

## Affected
- PyPI: `django-cms` — affected >=3.11.7 <3.11.9
- PyPI: `django-cms` — affected >=4.1.2 <4.1.4

## Details
Improper Neutralization of Input During Web Page Generation (XSS or 'Cross-site Scripting') vulnerability in django CMS Association django-cms allows Cross-Site Scripting (XSS).This issue affects django-cms: 3.11.7, 3.11.8, 4.1.2, 4.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11319
- https://github.com/django-cms/django-cms/commit/241d1cbe47a68f5d271ce4d27ad5e32e2c360ec3
- https://github.com/django-cms/django-cms
- https://github.com/pypa/advisory-database/tree/main/vulns/django-cms/PYSEC-2024-124.yaml
- https://iltosec.com/blog/post/django-cms-413-stored-xss-vulnerability-exploiting-the-page-title-field
- https://siberguvenlik.gov.tr/guvenlik-bildirimleri/detay/tr-24-1859
- https://www.django-cms.org/en/blog/2024/11/13/django-cms-security-update
- https://www.usom.gov.tr/bildirim/tr-24-1859
