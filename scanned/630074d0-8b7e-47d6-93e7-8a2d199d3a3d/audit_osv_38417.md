# [H] Flarum < 1.8.16 Session Persistence via Improper Access Token Revocation

## Summary
Severity: High
Advisory: CVE-2026-39924
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-39924
Type: osv

## Details
Flarum before 1.8.16 contains an improper session invalidation vulnerability that allows attackers who hold a valid session token to retain full account access after a victim changes their password, because the access_tokens table is never cleared on password change events. The TokensClearer::clearPasswordTokens() function only removes rows from the password_tokens table while leaving all active session cookies and API bearer tokens intact, including long-lived RememberAccessToken entries, and administrator-forced password resets via the user update endpoint are equally ineffective at revoking attacker-held sessions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39924.json
- https://github.com/flarum/framework/releases/tag/v1.8.16
- https://nvd.nist.gov/vuln/detail/CVE-2026-39924
- https://www.vulncheck.com/advisories/flarum-session-persistence-via-improper-access-token-revocation
- https://github.com/flarum/framework/pull/4546
- https://github.com/flarum/framework/commit/5f080293a029d0d273eb9678d597c74ea86a3bcc
- https://github.com/flarum/framework
