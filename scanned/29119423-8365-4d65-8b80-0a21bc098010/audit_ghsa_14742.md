# [H] djoser Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-v49p-m6gh-747c
CVE: CVE-2024-21543
CWE: CWE-287, CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-12-13
Source: https://github.com/advisories/GHSA-v49p-m6gh-747c
Type: github-advisory

## Affected
- PyPI: `djoser` — affected >=0 <2.3.0

## Details
Versions of the package djoser before 2.3.0 are vulnerable to Authentication Bypass when the authenticate() function fails. This is because the system falls back to querying the database directly, granting access to users with valid credentials, and eventually bypassing custom authentication checks such as two-factor authentication, LDAP validations, or requirements from configured AUTHENTICATION_BACKENDS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21543
- https://github.com/sunscrapers/djoser/issues/795
- https://github.com/sunscrapers/djoser/pull/819
- https://github.com/sunscrapers/djoser/commit/d33c3993c0c735f23cbedc60fa59fce69354f19d
- https://github.com/pypa/advisory-database/tree/main/vulns/djoser/PYSEC-2024-158.yaml
- https://github.com/sunscrapers/djoser
- https://github.com/sunscrapers/djoser/releases/tag/2.3.0
- https://lists.debian.org/debian-lts-announce/2025/02/msg00023.html
- https://security.snyk.io/vuln/SNYK-PYTHON-DJOSER-8366540
