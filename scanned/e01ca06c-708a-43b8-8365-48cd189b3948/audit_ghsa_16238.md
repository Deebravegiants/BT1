# [H] Django denial-of-service attack in the intcomma template filter

## Summary
Severity: High
Advisory: GHSA-xxj9-f6rv-m3x4
CVE: CVE-2024-24680
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-xxj9-f6rv-m3x4
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2 <3.2.24
- PyPI: `Django` — affected >=4.2 <4.2.10
- PyPI: `Django` — affected >=5.0 <5.0.2

## Details
An issue was discovered in Django 3.2 before 3.2.24, 4.2 before 4.2.10, and Django 5.0 before 5.0.2. The intcomma template filter was subject to a potential denial-of-service attack when used with very long strings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24680
- https://github.com/django/django/commit/16a8fe18a3b81250f4fa57e3f93f0599dc4895bc
- https://github.com/django/django/commit/55519d6cf8998fe4c8f5c8abffc2b10a7c3d14e9
- https://github.com/django/django/commit/572ea07e84b38ea8de0551f4b4eda685d91d09d2
- https://github.com/django/django/commit/c1171ffbd570db90ca206c30f8e2b9f691243820
- https://docs.djangoproject.com/en/5.0/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2024-28.yaml
- https://groups.google.com/forum/#%21forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D2JIRXEDP4ZET5KFMAPPYSK663Q52NEX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SN2PLJGYSAAG5KUVIUFJYKD3BLQ4OSN6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQJOMNRMVPCN5WMIZ7YSX5LQ7IR2NY4D
- https://www.djangoproject.com/weblog/2024/feb/06/security-releases
