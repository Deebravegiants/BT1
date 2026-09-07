# [H] Django cross-site request forgery (CSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-r5cj-wv24-92p5
CVE: CVE-2008-3909
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-r5cj-wv24-92p5
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0.91.0 <0.91.3
- PyPI: `Django` — affected >=0.95.0 <0.95.4
- PyPI: `Django` — affected >=0.96.0 <0.96.3

## Details
The administration application in Django 0.91.x, 0.95.x, and 0.96.x stores unauthenticated HTTP POST requests and processes them after successful authentication occurs, which allows remote attackers to conduct cross-site request forgery (CSRF) attacks and delete or modify data via unspecified requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-3909
- https://github.com/django/django/commit/44debfeaa4473bd28872c735dd3d9afde6886752
- https://github.com/django/django/commit/7e0972bded362bc4b851c109df2c8a6548481a8e
- https://github.com/django/django/commit/aee48854a164382c655acb9f18b3c06c3d238e81
- https://bugzilla.redhat.com/show_bug.cgi?id=460966
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2008-2.yaml
- https://www.redhat.com/archives/fedora-package-announce/2008-September/msg00091.html
- https://www.redhat.com/archives/fedora-package-announce/2008-September/msg00131.html
- http://www.debian.org/security/2008/dsa-1640
- http://www.djangoproject.com/weblog/2008/sep/02/security
- http://www.openwall.com/lists/oss-security/2008/09/03/4
