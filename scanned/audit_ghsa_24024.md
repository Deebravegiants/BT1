# [H] Django Admin Media Handler Vulnerable to Directory Traversal

## Summary
Severity: High
Advisory: GHSA-9xg7-gg9m-rmq9
CVE: CVE-2009-2659
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-9xg7-gg9m-rmq9
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0.96.0 <0.96.4
- PyPI: `Django` — affected >=1.0 <1.0.3

## Details
The Admin media handler in `core/servers/basehttp.py` in Django 1.0 and 0.96 does not properly map URL requests to expected "static media files," which allows remote attackers to conduct directory traversal attacks and read arbitrary files via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-2659
- https://github.com/django/django/commit/da85d76fd6ca846f3b0ff414e042ddb5e62e2e69
- https://github.com/django/django/commit/df7f917b7f51ba969faa49d000ffc79572c5dcb4
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2009-3.yaml
- https://web.archive.org/web/20111211001428/http://www.securityfocus.com/bid/35859
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00055.html
- https://www.redhat.com/archives/fedora-package-announce/2009-August/msg00069.html
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=539134
- http://code.djangoproject.com/changeset/11353
- http://www.djangoproject.com/weblog/2009/jul/28/security
- http://www.openwall.com/lists/oss-security/2009/07/29/2
