# [M] 4gaBoards: Mass Information Disclosure (Internal PII Leakage) on /api/users to any authenticated user

## Summary
Severity: Medium
Advisory: CVE-2026-53959
Aliases: GHSA-p77f-p47g-h72p
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-53959
Type: osv

## Details
4gaBoards is a boards system for realtime project management. Prior to 3.3.9, 4gaBoards allows any authenticated user to enumerate account information for every user through GET /api/users and retrieve arbitrary accounts through GET /api/users/:id. The users/index and users/show actions rely only on the default is-authenticated policy in server/config/policies.js, and server/api/controllers/users/index.js returns the result of sails.helpers.users.getMany() without requester-specific authorization or response sanitization. Responses expose email, phone, organization, name, isAdmin, ssoGoogleEmail, ssoGithubEmail, and other SSO-linked email fields, including data for administrators. This enables instance-wide user enumeration, privacy loss, and targeted phishing reconnaissance. This issue is fixed in version 3.3.9.

## References
- https://github.com/RARgames/4gaBoards/releases/tag/v3.3.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53959.json
- https://github.com/RARgames/4gaBoards/security/advisories/GHSA-p77f-p47g-h72p
- https://nvd.nist.gov/vuln/detail/CVE-2026-53959
- https://github.com/RARgames/4gaBoards/commit/93099d913cbfdbb1799b4aca19d2d0c2d2a276fb
