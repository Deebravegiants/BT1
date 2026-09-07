# [H] Uncontrolled Memory Consumption in Django

## Summary
Severity: High
Advisory: GHSA-wh4h-v3f2-r2pp
CVE: CVE-2019-6975
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-02-12
Source: https://github.com/advisories/GHSA-wh4h-v3f2-r2pp
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.11 <1.11.19
- PyPI: `Django` — affected >=2.0 <2.0.11
- PyPI: `Django` — affected >=2.1 <2.1.6

## Details
Django 1.11.x before 1.11.19, 2.0.x before 2.0.11, and 2.1.x before 2.1.6 allows Uncontrolled Memory Consumption via a malicious attacker-supplied value to the `django.utils.numberformat.format()` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6975
- https://github.com/django/django/commit/0bbb560183fabf0533289700845dafa94951f227
- https://github.com/django/django/commit/1f42f82566c9d2d73aff1c42790d6b1b243f7676
- https://github.com/django/django/commit/40cd19055773705301c3428ed5e08a036d2091f3
- https://www.openwall.com/lists/oss-security/2019/02/11/1
- https://www.djangoproject.com/weblog/2019/feb/11/security-releases
- https://www.debian.org/security/2019/dsa-4476
- https://web.archive.org/web/20200227084713/http://www.securityfocus.com/bid/106964
- https://usn.ubuntu.com/3890-1
- https://seclists.org/bugtraq/2019/Jul/10
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVXDOVCXLD74SHR2BENGCE2OOYYYWJHZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/66WMXHGBXD7GSM3PEXVCMCAGLMQYHZCU
- https://groups.google.com/forum/#!topic/django-announce/WTwEAprR0IQ
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2019-18.yaml
- https://github.com/django/django
- https://github.com/advisories/GHSA-wh4h-v3f2-r2pp
- https://docs.djangoproject.com/en/dev/releases/security
