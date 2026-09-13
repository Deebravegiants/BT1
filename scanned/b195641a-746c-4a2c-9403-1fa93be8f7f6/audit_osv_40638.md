# [H] 4gaBoards: SSO Pre-Account Takeover / Hijacking via Mass Assignment

## Summary
Severity: High
Advisory: CVE-2026-53958
Aliases: GHSA-j2fw-r2gj-hfr3
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-53958
Type: osv

## Details
4gaBoards is a boards system for realtime project management. Prior to 3.3.9, 4gaBoards allows an authenticated user to modify ssoGoogleId, ssoGoogleEmail, ssoGithubId, ssoGithubUsername, ssoGithubEmail, ssoMicrosoftId, ssoMicrosoftEmail, ssoOidcId, and ssoOidcEmail through PATCH /api/users/:id. The whitelist in server/api/controllers/users/update.js mass assigns these backend-managed identity attributes from user input. An attacker can place a victim's provider identifier on an attacker-controlled account, causing the default lookup in helpers such as server/api/helpers/users/get-create-one-for-github-sso.js to match the victim's first SSO login to the attacker's account before the email-linkage flow runs. The victim is logged into the attacker-controlled account, and projects, boards, or data the victim creates remain accessible through the attacker's original local credentials. This issue is fixed in version 3.3.9.

## References
- https://github.com/RARgames/4gaBoards/releases/tag/v3.3.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53958.json
- https://github.com/RARgames/4gaBoards/security/advisories/GHSA-j2fw-r2gj-hfr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-53958
- https://github.com/RARgames/4gaBoards/commit/7a79f4c5d338614058515752abd67e49ee2818bb
