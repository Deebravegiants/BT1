# [C] Django bypasses validation when using one form field to upload multiple files

## Summary
Severity: Critical
Advisory: GHSA-r3xc-prgr-mg9p
CVE: CVE-2023-31047
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-07
Source: https://github.com/advisories/GHSA-r3xc-prgr-mg9p
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2a1 <3.2.19
- PyPI: `Django` — affected >=4.0a1 <4.1.9
- PyPI: `Django` — affected >=4.2a1 <4.2.1

## Details
In Django 3.2 before 3.2.19, 4.x before 4.1.9, and 4.2 before 4.2.1, it was possible to bypass validation when using one form field to upload multiple files. This multiple upload has never been supported by forms.FileField or forms.ImageField (only the last uploaded file was validated). However, Django's "Uploading multiple files" documentation suggested otherwise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31047
- https://github.com/django/django/commit/21b1b1fc03e5f9e9f8c977ee6e35618dd3b353dd
- https://github.com/django/django/commit/e7c3a2ccc3a562328600be05068ed9149e12ce64
- https://github.com/django/django/commit/eed53d0011622e70b936e203005f0e6f4ac48965
- https://docs.djangoproject.com/en/4.2/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2023-61.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A45VKTUVQ2BN6D5ZLZGCM774R6QGFOHW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DNEHD6N435OE2XUFGDAAVAXSYWLCUBFD
- https://security.netapp.com/advisory/ntap-20230609-0008
- https://www.djangoproject.com/weblog/2023/may/03/security-releases
