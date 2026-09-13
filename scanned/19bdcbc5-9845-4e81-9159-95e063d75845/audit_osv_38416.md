# [C] Flarum < 1.8.16 Password Reset Token Expiry Bypass via POST /reset

## Summary
Severity: Critical
Advisory: CVE-2026-39923
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-39923
Type: osv

## Details
Flarum before 1.8.16 contains a password reset token expiry bypass vulnerability that allows unauthenticated attackers to reuse expired password reset tokens by submitting them directly to the reset processing endpoint. The SavePasswordController::handle() method calls PasswordToken::findOrFail() without performing any expiry validation, allowing attackers to bypass the 24-hour token lifetime enforced only during form rendering and change any account's password to gain an authenticated session.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39923.json
- https://github.com/flarum/framework/releases/tag/v1.8.16
- https://nvd.nist.gov/vuln/detail/CVE-2026-39923
- https://www.vulncheck.com/advisories/flarum-password-reset-token-expiry-bypass-via-post-reset
- https://github.com/flarum/framework/pull/4545
- https://github.com/flarum/framework/commit/2803058d0f9dc38252326070b46d4484fe5a857d
- https://github.com/flarum/framework
