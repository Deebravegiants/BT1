# [H] Memos 0.26.0 through 0.30.0 Insufficient Session Expiration on Password Change

## Summary
Severity: High
Advisory: CVE-2026-84203
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84203
Type: osv

## Details
Memos versions 0.26.0 through 0.30.0 fail to revoke refresh tokens when a user changes their password, allowing attackers to maintain account access. An attacker with a stolen refresh token can call the RefreshToken RPC to obtain new access tokens and rotate the refresh token indefinitely, bypassing the password change security measure.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84203.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84203
- https://www.vulncheck.com/advisories/memos-0.26.0-through-0.30.0-insufficient-session-expiration-on-password-change
- https://github.com/usememos/memos
- https://github.com/usememos/memos/blob/v0.30.0/server/auth/authenticator.go
- https://github.com/usememos/memos/blob/v0.30.0/server/router/api/v1/user_service.go
