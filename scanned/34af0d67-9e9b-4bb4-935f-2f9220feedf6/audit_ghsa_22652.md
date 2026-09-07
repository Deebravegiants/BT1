# [M] Django denial of service via empty session record creation

## Summary
Severity: Medium
Advisory: GHSA-pgxh-wfw4-jx2v
CVE: CVE-2015-5963
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pgxh-wfw4-jx2v
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.8 <1.8.4
- PyPI: `Django` — affected >=1.7 <1.7.10
- PyPI: `Django` — affected >=1.4 <1.4.22

## Details
`contrib.sessions.middleware.SessionMiddleware` in Django 1.8.x before 1.8.4, 1.7.x before 1.7.10, 1.4.x before 1.4.22, and possibly other versions allows remote attackers to cause a denial of service (session store consumption or session record removal) via a large number of requests to `contrib.auth.views.logout`, which triggers the creation of an empty session record.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5963
- https://github.com/django/django/commit/2eb86b01d7b59be06076f6179a454d0fd0afaff6
- https://github.com/django/django/commit/2f5485346ee6f84b4e52068c04e043092daf55f7
- https://github.com/django/django/commit/575f59f9bc7c59a5e41a081d1f5f55fc859c5012
- https://github.com/django/django/commit/8cc41ce7a7a8f6bebfdd89d5ab276cd0109f4fc5
- https://access.redhat.com/errata/RHSA-2015:1876
- https://github.com/django/django
- https://github.com/django/django/blob/4555a823fd57e261e1b19c778429473256c8ea08/docs/releases/1.8.4.txt#L9-L21
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-22.yaml
- https://web.archive.org/web/20150904151934/http://www.securitytracker.com/id/1033318
- https://web.archive.org/web/20200228050526/http://www.securityfocus.com/bid/76428
- https://www.djangoproject.com/weblog/2015/aug/18/security-releases
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/172084.html
- http://lists.opensuse.org/opensuse-updates/2015-09/msg00026.html
- http://lists.opensuse.org/opensuse-updates/2015-09/msg00035.html
- http://rhn.redhat.com/errata/RHSA-2015-1766.html
- http://rhn.redhat.com/errata/RHSA-2015-1767.html
- http://rhn.redhat.com/errata/RHSA-2015-1894.html
- http://www.debian.org/security/2015/dsa-3338
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
