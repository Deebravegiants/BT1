# [C] Django user with hardcoded password created when running tests on Oracle

## Summary
Severity: Critical
Advisory: GHSA-mv8g-fhh6-6267
CVE: CVE-2016-9013
CWE: CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mv8g-fhh6-6267
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.10a1 <1.10.3
- PyPI: `Django` — affected >=1.9a1 <1.9.11
- PyPI: `Django` — affected >=1.8a1 <1.8.16

## Details
Django 1.8.x before 1.8.16, 1.9.x before 1.9.11, and 1.10.x before 1.10.3 use a hardcoded password for a temporary database user created when running tests with an Oracle database, which makes it easier for remote attackers to obtain access to the database server by leveraging failure to manually specify a password in the database settings TEST dictionary.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9013
- https://github.com/django/django/commit/34e10720d81b8d407aa14d763b6a7fe8f13b4f2e
- https://github.com/django/django/commit/4844d86c7728c1a5a3bbce4ad336a8d32304072b
- https://github.com/django/django/commit/70f99952965a430daf69eeb9947079aae535d2d0
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2016-17.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OG5ROMUPS6C7BXELD3TAUUH7OBYV56WQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QXDKJYHN74BWY3P7AR2UZDVJREQMRE6S
- https://www.djangoproject.com/weblog/2016/nov/01/security-releases
- http://www.debian.org/security/2017/dsa-3835
- http://www.ubuntu.com/usn/USN-3115-1
