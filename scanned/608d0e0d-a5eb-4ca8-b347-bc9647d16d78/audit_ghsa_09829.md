# [H] Nginx-UI: Disabled users retain full API access through previously issued bearer tokens

## Summary
Severity: High
Advisory: GHSA-x234-x5vq-cc2v
CVE: CVE-2026-33031
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-x234-x5vq-cc2v
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0 <1.9.10-0.20260314152518-7b66578adb47

## Details
### Summary

A user who was disabled by an administrator can use previously issued API tokens for up to the token lifetime. In practice, disabling a compromised account does not actually terminate that user’s access, so an attacker who already stole a JWT can continue reading and modifying protected resources after the account is marked disabled.

Since tokens can be used to create new accounts, it is possible the disabled user to maintain the privilege.

### Details

The application exposes an account-level disable control through the users management API. Login process correctly enforces that control:
https://github.com/0xJacky/nginx-ui/blob/6ec542fd97abf2c5950f374f78a32938ad0030e6/internal/user/login.go#L29-L31

However, token-based authentication does not enforce the same check (This code validates token structure and expiry, but returns that user object without checking `user.Status`.):
https://github.com/0xJacky/nginx-ui/blob/6ec542fd97abf2c5950f374f78a32938ad0030e6/internal/user/user.go#L44-L139

There’s also no token revocation feature, unlike when a password is changed:
https://github.com/0xJacky/nginx-ui/blob/6ec542fd97abf2c5950f374f78a32938ad0030e6/api/user/user.go#L38-L51

As a result, a disabled user can continue to have full API access. In particular, since that includes account creation, they can create a new account and keep operating even after the JWT expires.

### PoC

The issue was validated with version 2.3.3 using the `uozi/nginx-ui:sha-c92ec0a` docker image.

View the PoC video:


https://github.com/user-attachments/assets/7a5175cb-2f79-4c1b-adad-e7d0bf2ea2bd



### Impact

Administrators who rely on "disable user" as an authentication or authorization control can be bypassed.

The disabled user can keep reading sensitive configuration and executing authenticated state-changing actions allowed to that account.

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-x234-x5vq-cc2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33031
- https://github.com/0xJacky/nginx-ui/commit/7b66578adb47bbec839b621a4666495249379174
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.4
