# [M] SimpleChat: Authenticated users can access other users' profile metadata through user IDOR endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-57205
Aliases: GHSA-x2jq-2m5m-65m4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-57205
Type: osv

## Details
SimpleChat is a secure AI conversation application with personal and group workspaces for document-grounded interactions. Prior to 0.241.203, the authenticated GET /api/user/info/<user_id> and GET /api/user/profile-image/<user_id> endpoints in application/single_app/route_backend_users.py accepted a caller-supplied user_id and read the matching Cosmos DB user-settings document without object-level authorization, allowing a low-privilege authenticated user to retrieve another user's email address, display name, and profile image. This issue is fixed in version 0.241.203.

## References
- https://github.com/microsoft/simplechat/blob/main/docs/explanation/fixes/USER_PROFILE_IDOR_AUTHORIZATION_FIX.md
- https://github.com/microsoft/simplechat/releases/tag/v0.250.001
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57205.json
- https://github.com/microsoft/simplechat/security/advisories/GHSA-x2jq-2m5m-65m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-57205
