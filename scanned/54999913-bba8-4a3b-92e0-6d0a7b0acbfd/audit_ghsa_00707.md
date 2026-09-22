# [H] Data leakage via cache key collision in Django

## Summary
Severity: High
Advisory: GHSA-wpjr-j57x-wxfw
CVE: CVE-2020-13254
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-wpjr-j57x-wxfw
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2 <2.2.13
- PyPI: `Django` — affected >=3.0 <3.0.7

## Details
An issue was discovered in Django version 2.2 before 2.2.13 and 3.0 before 3.0.7. In cases where a memcached backend does not perform key validation, passing malformed cache keys could result in a key collision, and potential data leakage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13254
- https://github.com/django/django/commit/07e59caa02831c4569bbebb9eb773bdd9cb4b206
- https://github.com/django/django/commit/84b2da5552e100ae3294f564f6c862fef8d0e693
- https://docs.djangoproject.com/en/3.0/releases/security
- https://github.com/advisories/GHSA-wpjr-j57x-wxfw
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2020-31.yaml
- https://groups.google.com/d/msg/django-announce/pPEmb2ot4Fo/X-SMalYSBAAJ
- https://lists.debian.org/debian-lts-announce/2020/06/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4A2AP4T7RKPBCLTI2NNQG3T6MINDUUMZ
- https://security.netapp.com/advisory/ntap-20200611-0002
- https://usn.ubuntu.com/4381-1
- https://usn.ubuntu.com/4381-2
- https://www.debian.org/security/2020/dsa-4705
- https://www.djangoproject.com/weblog/2020/jun/03/security-releases
- https://www.oracle.com/security-alerts/cpujan2021.html
