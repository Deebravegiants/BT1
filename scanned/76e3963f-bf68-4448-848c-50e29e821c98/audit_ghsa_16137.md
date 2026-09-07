# [M] django CMS Attributes Field Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-vxcv-4xvf-pc22
CVE: CVE-2024-11406
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-vxcv-4xvf-pc22
Type: github-advisory

## Affected
- PyPI: `djangocms-attributes-field` — affected >=0 <4.0.0

## Details
Improper Neutralization of Input During Web Page Generation (XSS or 'Cross-site Scripting') vulnerability in django CMS Association django CMS Attributes Fields allows Stored XSS.This issue affects django CMS Attributes Fields: before 4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11406
- https://github.com/django-cms/djangocms-attributes-field/commit/fe68d29ab78db5885bc31b67cf0537f1f02b33ad
- https://github.com/django-cms/djangocms-attributes-field
- https://iltosec.com/blog/post/djangocms-attributes-field-300-stored-xss-vulnerability
- https://pypi.org/project/djangocms-attributes-field/#history
- https://siberguvenlik.gov.tr/guvenlik-bildirimleri/detay/tr-24-1864
- https://www.django-cms.org/en/blog/2024/11/19/security-updates-for-django-filer-and-django-cms-attributes-field
- https://www.usom.gov.tr/bildirim/tr-24-1864
