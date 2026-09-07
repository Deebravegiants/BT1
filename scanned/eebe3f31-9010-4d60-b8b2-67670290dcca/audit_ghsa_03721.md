# [H] Improper Input Validation in Django

## Summary
Severity: High
Advisory: GHSA-337x-4q8g-prc5
CVE: CVE-2019-3498
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-01-14
Source: https://github.com/advisories/GHSA-337x-4q8g-prc5
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.11a1 <1.11.18
- PyPI: `Django` — affected >=2.0a1 <2.0.10
- PyPI: `Django` — affected >=2.1a1 <2.1.5

## Details
In Django 1.11.x before 1.11.18, 2.0.x before 2.0.10, and 2.1.x before 2.1.5, an Improper Neutralization of Special Elements in Output Used by a Downstream Component issue exists in `django.views.defaults.page_not_found()`, leading to content spoofing (in a 404 error page) if a user fails to recognize that a crafted URL has malicious content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3498
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/advisories/GHSA-337x-4q8g-prc5
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2019-17.yaml
- https://groups.google.com/forum/#!topic/django-announce/VYU7xQQTEPQ
- https://lists.debian.org/debian-lts-announce/2019/01/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVXDOVCXLD74SHR2BENGCE2OOYYYWJHZ
- https://usn.ubuntu.com/3851-1
- https://web.archive.org/web/20200227094237/http://www.securityfocus.com/bid/106453
- https://www.debian.org/security/2019/dsa-4363
- https://www.djangoproject.com/weblog/2019/jan/04/security-releases
