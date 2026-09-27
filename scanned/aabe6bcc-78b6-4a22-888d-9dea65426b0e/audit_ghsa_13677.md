# [H] Django potential denial of service vulnerability in UsernameField on Windows

## Summary
Severity: High
Advisory: GHSA-qmf9-6jqf-j8fq
CVE: CVE-2023-46695
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-02
Source: https://github.com/advisories/GHSA-qmf9-6jqf-j8fq
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2a1 <3.2.23
- PyPI: `Django` — affected >=4.1a1 <4.1.13
- PyPI: `Django` — affected >=4.2a1 <4.2.7

## Details
An issue was discovered in Django 3.2 before 3.2.23, 4.1 before 4.1.13, and 4.2 before 4.2.7. The NFKC normalization is slow on Windows. As a consequence, django.contrib.auth.forms.UsernameField is subject to a potential DoS (denial of service) attack via certain inputs with a very large number of Unicode characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46695
- https://github.com/django/django/commit/048a9ebb6ea468426cb4e57c71572cbbd975517f
- https://github.com/django/django/commit/4965bfdde2e5a5c883685019e57d123a3368a75e
- https://github.com/django/django/commit/f9a7fb8466a7ba4857eaf930099b5258f3eafb2b
- https://docs.djangoproject.com/en/4.2/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2023-222.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://groups.google.com/forum/#%21forum/django-announce
- https://security.netapp.com/advisory/ntap-20231214-0001
- https://www.djangoproject.com/weblog/2023/nov/01/security-releases
