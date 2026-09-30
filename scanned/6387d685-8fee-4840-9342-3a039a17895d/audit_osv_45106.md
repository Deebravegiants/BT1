# [M] webhookd: Unrestricted HTTP Header to Shell Variable Injection

## Summary
Severity: Medium
Advisory: GHSA-v25g-mvwr-f5fp
Aliases: CVE-2026-59157
Ecosystem: Go
Published: 2026-09-09
Source: https://osv.dev/vulnerability/GHSA-v25g-mvwr-f5fp
Type: osv

## Affected
- Go: `github.com/ncarlier/webhookd` — affected >=0 <1.22.0

## Details
## Description
Before 1.22, if the Basic Auth (`htpasswd`) middleware was not configured, all incoming HTTP headers were blindly forwarded to the webhook script execution environment as shell variables. While the Basic Auth middleware correctly strips the authentication header (`X-WebAuthn-User`) from the incoming request before conditionally re-injecting it on successful authentication, disabling Basic Auth left the system vulnerable if deployed behind an unhardened reverse proxy.

## Impact
If an upstream reverse proxy is not properly hardened to strip client-provided authentication headers, an attacker could manually supply these headers (e.g., `X-WebAuthn-User`). A webhook script relying on this forwarded header for privilege elevation or identity verification could therefore be exploited to bypass security controls and impersonate other users.

## Mitigation
The `WHD_ALLOWED_UPSTREAM_HEADERS` configuration setting has been introduced to enforce a strict allowlist of HTTP headers that can be converted into shell variables. 

Additionally, the default behavior has been changed to adhere to the principle of least privilege. It is no longer `*` (allow all). The default allowed headers are now restricted to standard operational headers:
`Accept,Content-Type,Content-Length,User-Agent,X-Forwarded-For`

Administrators relying on upstream authentication proxies must explicitly add their authentication headers (e.g., `WHD_ALLOWED_UPSTREAM_HEADERS="Accept,Content-Type,Content-Length,User-Agent,X-Forwarded-For,x-webauthn-user"`) to ensure they are passed to the scripts securely.

## References
- https://github.com/ncarlier/webhookd/security/advisories/GHSA-v25g-mvwr-f5fp
- https://github.com/ncarlier/webhookd
- https://github.com/ncarlier/webhookd/releases/tag/v1.22.0
