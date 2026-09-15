# [M] Django Denial of service vulnerability in django.utils.encoding.uri_to_iri

## Summary
Severity: Medium
Advisory: GHSA-7h4p-27mh-hmrw
CVE: CVE-2023-41164
CWE: CWE-1284, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-7h4p-27mh-hmrw
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2 <3.2.21
- PyPI: `Django` — affected >=4.1 <4.1.11
- PyPI: `Django` — affected >=4.2 <4.2.5

## Details
In Django 3.2 before 3.2.21, 4.1 before 4.1.11, and 4.2 before 4.2.5, django.utils.encoding.uri_to_iri() is subject to a potential DoS (denial of service) attack via certain inputs with a very large number of Unicode characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41164
- https://github.com/django/django/commit/6f030b1149bd8fa4ba90452e77cb3edc095ce54e
- https://github.com/django/django/commit/9c51b4dcfa0cefcb48231f4d71cafa80821f87b9
- https://github.com/django/django/commit/ba00bc5ec6a7eff5e08be438f7b5b0e9574e8ff0
- https://docs.djangoproject.com/en/4.2/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2023-225.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://groups.google.com/forum/#%21forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HJFRPUHDYJHBH3KYHSPGULQM4JN7BMSU
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQJOMNRMVPCN5WMIZ7YSX5LQ7IR2NY4D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HJFRPUHDYJHBH3KYHSPGULQM4JN7BMSU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQJOMNRMVPCN5WMIZ7YSX5LQ7IR2NY4D
- https://security.netapp.com/advisory/ntap-20231214-0002
- https://www.djangoproject.com/weblog/2023/sep/04/security-releases
