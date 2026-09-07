# [H] Denial-of-service in Django

## Summary
Severity: High
Advisory: GHSA-53qw-q765-4fww
CVE: CVE-2021-45115
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-53qw-q765-4fww
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2a1 <2.2.26
- PyPI: `Django` — affected >=3.2a1 <3.2.11
- PyPI: `Django` — affected >=4.0a1 <4.0.1

## Details
An issue was discovered in Django 2.2 before 2.2.26, 3.2 before 3.2.11, and 4.0 before 4.0.1. `UserAttributeSimilarityValidator` incurred significant overhead in evaluating a submitted password that was artificially large in relation to the comparison values. In a situation where access to user registration was unrestricted, this provided a potential vector for a denial-of-service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45115
- https://github.com/django/django/commit/2135637fdd5ce994de110affef9e67dffdf77277
- https://github.com/django/django/commit/a8b32fe13bcaed1c0b772fdc53de84abc224fb20
- https://github.com/django/django/commit/df79ef03ac867c93caaa6be56bc69e66abfeef8f
- https://docs.djangoproject.com/en/4.0/releases/security
- https://github.com/advisories/GHSA-53qw-q765-4fww
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2022-1.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://security.netapp.com/advisory/ntap-20220121-0005
- https://www.djangoproject.com/weblog/2022/jan/04/security-releases
