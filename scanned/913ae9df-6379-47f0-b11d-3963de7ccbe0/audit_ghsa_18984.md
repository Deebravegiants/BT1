# [H] Django has a denial-of-service vulnerability in HttpResponseRedirect and HttpResponsePermanentRedirect on Windows

## Summary
Severity: High
Advisory: GHSA-qw25-v68c-qjf3
CVE: CVE-2025-64458
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-05
Source: https://github.com/advisories/GHSA-qw25-v68c-qjf3
Type: github-advisory

## Affected
- PyPI: `django` — affected >=5.2a1 <5.2.8
- PyPI: `django` — affected >=5.0a1 <5.1.14
- PyPI: `django` — affected >=0 <4.2.26

## Details
An issue was discovered in 5.1 before 5.1.14, 4.2 before 4.2.26, and 5.2 before 5.2.8.
NFKC normalization in Python is slow on Windows. As a consequence, `django.http.HttpResponseRedirect`, `django.http.HttpResponsePermanentRedirect`, and the shortcut `django.shortcuts.redirect`  were subject to a potential  denial-of-service attack via certain inputs with a very large number of Unicode characters.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Seokchan Yoon for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64458
- https://github.com/django/django/commit/3790593781d26168e7306b5b2f8ea0309de16242
- https://github.com/django/django/commit/4f5d904b63751dea9ffc3b0e046404a7fa5881ac
- https://github.com/django/django/commit/6e13348436fccf8f22982921d6a3a3e65c956a9f
- https://github.com/django/django/commit/770eea38d7a0e9ba9455140b5a9a9e33618226a7
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2025-107.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2025/nov/05/security-releases
