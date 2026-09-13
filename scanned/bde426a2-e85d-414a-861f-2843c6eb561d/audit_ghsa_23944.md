# [H] Django database denial-of-service with ModelMultipleChoiceField

## Summary
Severity: High
Advisory: GHSA-6g95-x6cj-mg4v
CVE: CVE-2015-0222
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6g95-x6cj-mg4v
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.6 <1.6.10
- PyPI: `Django` — affected >=1.7 <1.7.3

## Details
ModelMultipleChoiceField in Django 1.6.x before 1.6.10 and 1.7.x before 1.7.3, when show_hidden_initial is set to True, allows remote attackers to cause a denial of service by submitting duplicate values, which triggers a large number of SQL queries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0222
- https://github.com/django/django/commit/bcfb47780ce7caecb409a9e9c1c314266e41d392
- https://github.com/django/django/commit/d7a06ee7e571b6dad07c0f5b519b1db02e2a476c
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-7.yaml
- https://web.archive.org/web/20161201073154/http://secunia.com/advisories/62285
- https://web.archive.org/web/20161201073337/http://secunia.com/advisories/62309
- https://www.djangoproject.com/weblog/2015/jan/13/security
- http://advisories.mageia.org/MGASA-2015-0026.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148485.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148608.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148696.html
- http://lists.opensuse.org/opensuse-updates/2015-04/msg00001.html
- http://lists.opensuse.org/opensuse-updates/2015-09/msg00035.html
- http://ubuntu.com/usn/usn-2469-1
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:109
