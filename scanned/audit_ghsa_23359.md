# [M] Buildbot CRLF Injection

## Summary
Severity: Medium
Advisory: GHSA-66x7-2r56-fj77
CVE: CVE-2019-7313
CWE: CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-66x7-2r56-fj77
Type: github-advisory

## Affected
- PyPI: `buildbot` — affected >=0.9.0 <1.8.1

## Details
`www/resource.py` in Buildbot before 1.8.1 allows CRLF injection in the Location header of `/auth/login` and `/auth/logout` via the redirect parameter. This affects other web sites in the same domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7313
- https://github.com/buildbot/buildbot/pull/4584
- https://github.com/buildbot/buildbot/commit/e781f110933e05ecdb30abc64327a2c7c9ff9c5a
- https://github.com/buildbot/buildbot
- https://github.com/buildbot/buildbot/wiki/CRLF-injection-in-Buildbot-login-and-logout-redirect-code
- https://github.com/pypa/advisory-database/tree/main/vulns/buildbot/PYSEC-2019-7.yaml
