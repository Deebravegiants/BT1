# [H] 4gaBoards: Pre-Account Takeover via SSO Email Linkage

## Summary
Severity: High
Advisory: CVE-2026-50191
Aliases: GHSA-f3p6-chc6-pc77
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50191
Type: osv

## Details
4gaBoards is a boards system for realtime project management. Prior to 3.3.8, 4gaBoards is vulnerable to pre-account takeover when registrationEnabled, localRegistrationEnabled, and ssoRegistrationEnabled are enabled and Google, GitHub, Microsoft, or OIDC SSO is configured. The POST /api/register endpoint permits creation of an unverified local account with a victim's email address, and POST /api/access-tokens permits that account to authenticate while isVerified is false. During the victim's first SSO login, server/api/helpers/users/get-create-one-for-github-sso.js, server/api/helpers/users/get-create-one-for-google-sso.js, server/api/helpers/users/get-create-one-for-microsoft-sso.js, and server/api/helpers/users/get-create-one-for-oidc-sso.js find the attacker-controlled account by email and link the verified SSO identity without confirming ownership of the local account. The attacker can retain local-password access to the linked account and obtain the victim's projects, data, and permissions. This issue is fixed in version 3.3.8.

## References
- https://github.com/RARgames/4gaBoards/releases/tag/v3.3.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50191.json
- https://github.com/RARgames/4gaBoards/security/advisories/GHSA-f3p6-chc6-pc77
- https://nvd.nist.gov/vuln/detail/CVE-2026-50191
- https://github.com/RARgames/4gaBoards/commit/484c92d583cfbc6815f96364071bb531ec594bf8
