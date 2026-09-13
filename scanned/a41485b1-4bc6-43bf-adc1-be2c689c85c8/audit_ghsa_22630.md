# [M] Django Middleware Enables Session Hijacking

## Summary
Severity: Medium
Advisory: GHSA-625g-gx8c-xcmg
CVE: CVE-2014-0482
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-625g-gx8c-xcmg
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.14
- PyPI: `Django` — affected >=1.5 <1.5.9
- PyPI: `Django` — affected >=1.6 <1.6.6
- PyPI: `Django` — affected >=1.7a1 <1.7c3

## Details
The `contrib.auth.middleware.RemoteUserMiddleware` middleware in Django before 1.4.14, 1.5.x before 1.5.9, 1.6.x before 1.6.6, and 1.7 before release candidate 3, when using the `contrib.auth.backends.RemoteUserBackend` backend, allows remote authenticated users to hijack web sessions via vectors related to the `REMOTE_USER` header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0482
- https://github.com/django/django/commit/0268b855f9eab3377f2821164ef3e66037789e09
- https://github.com/django/django/commit/5307ce565fbedb9cc27cbe7c757b41a00438d37c
- https://github.com/django/django/commit/c9e3b9949cd55f090591fbdc4a114fcb8368b6d9
- https://github.com/django/django/commit/dd68f319b365f6cb38c5a6c106faf4f6142d7d88
- https://github.com/django/django
- https://github.com/django/django/blob/aa3cb3f37265be37d892e2b391ff023e9caee2a4/docs/releases/1.5.9.txt#L42
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2014-6.yaml
- https://www.djangoproject.com/weblog/2014/aug/20/security
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00023.html
- http://www.debian.org/security/2014/dsa-3010
