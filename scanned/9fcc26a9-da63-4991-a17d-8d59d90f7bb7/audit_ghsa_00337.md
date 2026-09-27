# [C] Django-Anymail prone to a timing attack

## Summary
Severity: Critical
Advisory: GHSA-hxf9-7h4c-f5jv
CVE: CVE-2018-6596
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-hxf9-7h4c-f5jv
Type: github-advisory

## Affected
- PyPI: `django-anymail` — affected >=0 <1.2.1

## Details
webhooks/base.py in Anymail (aka django-anymail) before 1.2.1 is prone to a timing attack vulnerability on the WEBHOOK_AUTHORIZATION secret, which allows remote attackers to post arbitrary e-mail tracking events.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6596
- https://github.com/anymail/django-anymail/commit/c07998304b4a31df4c61deddcb03d3607a04691b
- https://github.com/anymail/django-anymail/commit/db586ede1fbb41dce21310ea28ae15a1cf1286c5
- https://bugs.debian.org/889450
- https://github.com/advisories/GHSA-hxf9-7h4c-f5jv
- https://github.com/anymail/django-anymail
- https://github.com/anymail/django-anymail/releases/tag/v1.2.1
- https://github.com/anymail/django-anymail/releases/tag/v1.3
- https://github.com/pypa/advisory-database/tree/main/vulns/django-anymail/PYSEC-2018-7.yaml
- https://www.debian.org/security/2018/dsa-4107
