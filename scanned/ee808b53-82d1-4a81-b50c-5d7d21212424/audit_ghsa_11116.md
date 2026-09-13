# [M] Bytebase vulnerable to Improper Authentication

## Summary
Severity: Medium
Advisory: GHSA-5r3p-6rj5-7937
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-5r3p-6rj5-7937
Type: github-advisory

## Affected
- Go: `github.com/bytebase/bytebase` — affected >=0 <1.0.1

## Details
### Impact
- GitLab login allows login by any user.
- JWT auth token can be derived as long as the server isn't rebooted.
- Developers can assign issues to non-admin/DBA users.

## References
- https://github.com/bytebase/bytebase/security/advisories/GHSA-5r3p-6rj5-7937
- https://github.com/bytebase/bytebase/commit/a578ed58e478ba5c2dadf8d538ec5c3d39c28461
- https://github.com/bytebase/bytebase
