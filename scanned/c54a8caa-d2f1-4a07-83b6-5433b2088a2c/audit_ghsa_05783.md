# [M] Traefik: ForwardAuth middleware leaks X-Forwarded-Port spoofing via untrusted X-Forwarded-Proto when trustForwardHeader=false

## Summary
Severity: Medium
Advisory: GHSA-3q9r-p662-5j8m
CVE: CVE-2026-54764
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-3q9r-p662-5j8m
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.51
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.22
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0 <3.7.6
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a medium severity vulnerability in Traefik's ForwardAuth middleware. Even when configured with `trustForwardHeader: false`, Traefik derives the `X-Forwarded-Port` header sent to the authentication service from the original incoming request instead of the sanitized forwarded request. As a result, an unauthenticated remote attacker can inject an `X-Forwarded-Proto: https` header over a plain HTTP connection and cause Traefik to forward `X-Forwarded-Port: 443` to the auth service, bypassing port-based authorization checks. This is a regression of the incomplete fix for GHSA-6384-m2mw-rf54, which addressed the `X-Forwarded-Proto` and `X-Forwarded-Prefix` spoofing vectors but missed the `X-Forwarded-Port` vector.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.51
- https://github.com/traefik/traefik/releases/tag/v3.6.22
- https://github.com/traefik/traefik/releases/tag/v3.7.6

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary

  The ForwardAuth middleware, even when configured with `trustForwardHeader: false`,
  still derives the `X-Forwarded-Port` header sent to the authentication service by
  reading the **attacker-controlled** `X-Forwarded-Proto` header from the original
  incoming request. This allows an unauthenticated remote attacker to cause Traefik
  to forward `X-Forwarded-Port: 443` to the auth service on a plain HTTP connection,
  creating an inconsistency that can bypass port-based authorization checks.

  ### Details

  The fix introduced in commit `5e1de2258` (released as part of the April 2026 security
  advisory GHSA-6384-m2mw-rf54) correctly strips all X-Forwarded-* headers from the
  forwarded auth request when `trustForwardHeader=false`, and reconstructs
  `X-Forwarded-Proto` from the actual TLS state of the connection (`req.TLS`).

  However, the reconstruction of `X-Forwarded-Port` is delegated to the helper
  `forwardedPort(req)` which receives the **original request** (`req`) rather than
  the sanitized forward request (`forwardReq`):

  ```go
  // pkg/middlewares/auth/forward.go – writeHeader()
  if !trustForwardHeader {
      forwardedheaders.DeleteXForwardedHeaders(forwardReq.Header) // strips all X-Fwd-* from forwardReq
  }
  // ...
  if _, ok := forwardReq.Header[forwardedheaders.XForwardedPort]; !ok {
      forwardReq.Header.Set(forwardedheaders.XForwardedPort, forwardedPort(req)) // ← req = ORIGINAL
  }

  // pkg/middlewares/auth/forward.go – forwardedPort()
  func forwardedPort(req *http.Request) string {
      if _, port, err := net.SplitHostPort(req.Host); err == nil && port != "" {
          return port
      }
      // Reads attacker-controlled header on the ORIGINAL request:
      if req.Header.Get(forwardedheaders.XForwardedProto) == "https" || ... {
          return "443"
      }
      if req.TLS != nil {
          return "443"
      }
      return "80"
  }

  Result when trustForwardHeader=false and attacker sends X-Forwarded-Proto: https
  on a plain HTTP connection:

  ┌──────────────────────────────────┬──────────┬────────┐
  │ Header forwarded to auth service │ Expected │ Actual │
  ├──────────────────────────────────┼──────────┼────────┤
  │ X-Forwarded-Proto                │ http     │ http ✓ │
  ├──────────────────────────────────┼──────────┼────────┤
  │ X-Forwarded-Port                 │ 80       │ 443 ✗  │
  └──────────────────────────────────┴──────────┴────────┘
```
  The inconsistency between Proto=http and Port=443 is exploitable against any
  authentication service that gates access based on X-Forwarded-Port.

  ### PoC

  Traefik configuration:

  ```http:
    middlewares:
      my-auth:
        forwardAuth:
          address: "http://auth-service/"
          trustForwardHeader: false  # security setting, but still bypassable
    routers:
      api:
        rule: "PathPrefix(`/api`)"
        middlewares:
          - my-auth
        service: backend

  Auth service logic (example victim):
  # auth-service checks: only port 443 requests are considered "secure"
  port = request.headers.get("X-Forwarded-Port", "80")
  proto = request.headers.get("X-Forwarded-Proto", "http")
  if port == "443":
      return 200  # grant access
  return 403
```
  Attack:

  Plain HTTP connection, no TLS – but spoofs port 443
  curl -H "X-Forwarded-Proto: https" http://traefik.example.com/api/admin
  Auth service receives X-Forwarded-Port: 443 → grants access

  Verification: Enable Traefik debug logging and observe X-Forwarded-Port: 443
  in the auth request while the connection is plain HTTP.

 ### Impact

  Any deployment using the ForwardAuth middleware with trustForwardHeader: false where
  the downstream authentication service uses X-Forwarded-Port to make authorization
  decisions is vulnerable to privilege escalation. An unauthenticated attacker can
  bypass port-based security checks (e.g., "only allow requests arriving on HTTPS port
  443") by injecting a single X-Forwarded-Proto: https header on a plain HTTP
  connection.

  This is a regression of the incomplete fix for GHSA-6384-m2mw-rf54: while the
  X-Forwarded-Prefix and X-Forwarded-Proto spoofing vectors were addressed, the
  X-Forwarded-Port vector was missed.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-3q9r-p662-5j8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-54764
- https://github.com/traefik/traefik/pull/13344
- https://github.com/traefik/traefik/commit/7ae92d8c2c10ac04ef5a03df0ed5019ce0f44b2d
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.51
- https://github.com/traefik/traefik/releases/tag/v3.6.22
- https://github.com/traefik/traefik/releases/tag/v3.7.6
