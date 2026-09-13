# [C] SQL injection in Django

## Summary
Severity: Critical
Advisory: GHSA-hmr4-m2h5-33qx
CVE: CVE-2020-7471
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-11
Source: https://github.com/advisories/GHSA-hmr4-m2h5-33qx
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.11.28
- PyPI: `Django` — affected >=2.0 <2.2.10
- PyPI: `Django` — affected >=3.0 <3.0.3

## Details
Django 1.11 before 1.11.28, 2.2 before 2.2.10, and 3.0 before 3.0.3 allows SQL Injection if untrusted data is used as a StringAgg delimiter (e.g., in Django applications that offer downloads of data as a series of rows with a user-specified column delimiter). By passing a suitably crafted delimiter to a contrib.postgres.aggregates.StringAgg instance, it was possible to break escaping and inject malicious SQL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7471
- https://github.com/django/django/commit/001b0634cd309e372edb6d7d95d083d02b8e37bd
- https://github.com/django/django/commit/505826b469b16ab36693360da9e11fd13213421b
- https://github.com/django/django/commit/c67a368c16e4680b324b4f385398d638db4d8147
- https://github.com/django/django/commit/eb31d845323618d688ad429479c6dda973056136
- https://www.openwall.com/lists/oss-security/2020/02/03/1
- https://www.djangoproject.com/weblog/2020/feb/03/security-releases
- https://www.debian.org/security/2020/dsa-4629
- https://usn.ubuntu.com/4264-1
- https://security.netapp.com/advisory/ntap-20200221-0006
- https://security.gentoo.org/glsa/202004-17
- https://seclists.org/bugtraq/2020/Feb/30
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4A2AP4T7RKPBCLTI2NNQG3T6MINDUUMZ
- https://groups.google.com/forum/#!topic/django-announce/X45S86X5bZI
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2020-35.yaml
- https://github.com/django/django
- https://github.com/advisories/GHSA-hmr4-m2h5-33qx
- https://docs.djangoproject.com/en/3.0/releases/security
- http://www.openwall.com/lists/oss-security/2020/02/03/1
