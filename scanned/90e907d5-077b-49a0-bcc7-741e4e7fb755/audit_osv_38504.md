# [H] Authenticated Movary User Can Self-Escalate to Administrator via PUT /settings/users/{userId} by Setting isAdmin=true

## Summary
Severity: High
Advisory: CVE-2026-40349
Aliases: GHSA-mcfq-8rx7-w25v
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40349
Type: osv

## Details
Movary is a self hosted web app to track and rate a user's watched movies. Prior to version 0.71.1, an ordinary authenticated user can escalate their own account to administrator by sending `isAdmin=true` to `PUT /settings/users/{userId}` for their own user ID. The endpoint is intended to let a user edit their own profile, but it updates the sensitive `isAdmin` field without any admin-only authorization check. Version 0.71.1 patches the issue.

## References
- https://github.com/leepeuker/movary/releases/tag/0.71.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40349.json
- https://github.com/leepeuker/movary/security/advisories/GHSA-mcfq-8rx7-w25v
- https://nvd.nist.gov/vuln/detail/CVE-2026-40349
- https://github.com/leepeuker/movary/commit/12c8a090051b1a1c07a3aa48922f3bc9ffe44c8b
- https://github.com/leepeuker/movary/pull/750
