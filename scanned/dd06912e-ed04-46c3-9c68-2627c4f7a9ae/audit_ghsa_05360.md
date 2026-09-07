# [M] nebula-mesh: Session and OIDC state cookies lack the Secure attribute

## Summary
Severity: Medium
Advisory: GHSA-rqfj-vv8r-xhqc
CVE: CVE-2026-48058
CWE: CWE-614
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-rqfj-vv8r-xhqc
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.2

## Details
`internal/web/session.go` and `internal/web/oidc.go` set `HttpOnly` and `SameSite=Lax` on every cookie but never `Secure`. A single plaintext request to the origin (operator on a LAN, mistyped URL, HTTP→HTTPS not strictly enforced, reverse proxy misconfiguration) discloses the session.

## Affected
All released versions up to v0.3.1.

## Impact
An attacker who can observe one HTTP request to the origin recovers the session cookie and impersonates the operator for the remainder of its 24h TTL. The OIDC state cookie has a narrower 10-minute window but enables CSRF on the OIDC callback during that window.

## Cookie sites
- `internal/web/session.go` — `Login`, `StartAuthenticatedSession`, `CompleteTwoFactor`, `Logout`
- `internal/web/oidc.go` — `HandleLogin` (state set), `HandleCallback` (state clear)

## Suggested fix
Driven by an explicit `cookie_secure` config option, inferred true when `tls_cert`+`tls_key` are configured and false otherwise. `rate_limit.trust_proxy_header` is deliberately not used as a signal — that flag controls XFF parsing for rate-limit IPs and does not promise the proxy speaks TLS to clients. Operator behind a TLS-terminating proxy sets `cookie_secure: true` explicitly.

Logout and OIDC state-clear cookies also pick up matching `HttpOnly` + `SameSite=Lax` so browsers reliably replace the original.

## Reproducer
Start `nebula-mgmt` without `tls_cert`/`tls_key` (the documented "behind a reverse proxy" deployment). Hit any login flow over the local listener:

```
curl -i -X POST -d 'username=admin&password=…' http://127.0.0.1:8080/ui/login
```

The `Set-Cookie: nebula_session=…` line will lack `Secure`. A subsequent unencrypted hop reveals the cookie verbatim.

## Operational migration
Operators flipping `cookie_secure` on a running deployment should expect a one-time logout: existing browser cookies have the old attribute set and the new delete-cookie won't match.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-rqfj-vv8r-xhqc
- https://github.com/forgekeep/nebula-mesh/commit/ffdd67dbf221d9a5855c39fbe11b49c245048d85
- https://github.com/juev/nebula-mesh
