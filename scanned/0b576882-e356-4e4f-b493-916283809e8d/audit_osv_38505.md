# [H] Movary User Management (/settings/users) has Authorization Bypass that Allows Low-Privileged Users to Enumerate All Users and Create Administrator Accounts

## Summary
Severity: High
Advisory: CVE-2026-40350
Aliases: GHSA-7r3f-9fwv-p43w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40350
Type: osv

## Details
Movary is a self hosted web app to track and rate a user's watched movies. Prior to version 0.71.1, an ordinary authenticated user can access the user-management endpoints `/settings/users` and use them to enumerate all users and create a new administrator account. This happens because the route definitions do not enforce admin-only middleware, and the controller-level authorization check uses a broken boolean condition. As a result, any user with a valid web session cookie can reach functionality that should be restricted to administrators. Version 0.71.1 patches the issue.

## References
- https://github.com/leepeuker/movary/releases/tag/0.71.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40350.json
- https://github.com/leepeuker/movary/security/advisories/GHSA-7r3f-9fwv-p43w
- https://nvd.nist.gov/vuln/detail/CVE-2026-40350
- https://github.com/leepeuker/movary/commit/92c7400486f5fe9f350046e04e45a8502778bf39
- https://github.com/leepeuker/movary/pull/749
