# [H] Ajenti has an authorization bypass during custom package installation

## Summary
Severity: High
Advisory: GHSA-73jv-44c3-j5p2
CVE: CVE-2026-35175
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-73jv-44c3-j5p2
Type: github-advisory

## Affected
- PyPI: `ajenti-panel` — affected >=0 <2.2.15

## Details
### Impact

An authenticated user (using the `auth_users` plugin authentication method) could install a custom package even if this user is not superuser.

### Patches

This is fixed in the version 2.2.15. Users should upgrade to this version as soon as possible.

## References
- https://github.com/ajenti/ajenti/security/advisories/GHSA-73jv-44c3-j5p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-35175
- https://github.com/ajenti/ajenti
- https://github.com/ajenti/ajenti/releases/tag/v2.2.15
