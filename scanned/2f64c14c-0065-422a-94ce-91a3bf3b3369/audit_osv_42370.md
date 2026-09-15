# [C] Serendipity < 2.6.1 Authentication Bypass via Username Collision

## Summary
Severity: Critical
Advisory: CVE-2026-67351
Aliases: GHSA-v645-243f-jwgh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67351
Type: osv

## Details
Serendipity before 2.6.1 contains an authentication context confusion vulnerability where password validation and session loading operate independently without ensuring both use the same user record. An authenticated Editor can create a username collision with an Administrator account and obtain administrative privileges by logging in with their own password while the session loads the Administrator's account data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67351.json
- https://github.com/s9y/Serendipity/security/advisories/GHSA-v645-243f-jwgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-67351
- https://www.vulncheck.com/advisories/serendipity-authentication-bypass-via-username-collision
