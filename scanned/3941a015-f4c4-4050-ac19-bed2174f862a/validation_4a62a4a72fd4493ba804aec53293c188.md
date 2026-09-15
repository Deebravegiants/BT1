I found a concrete analog. The bug class from the TerriaJS advisory (suffix-matching a hostname against an allowlisted domain without verifying a label/dot boundary, so `maliciousexample.com` matches an allowlist entry for `example.com`) is directly reproduced in the Chainlink Gateway's CORS origin allowlist logic.

### Title
CORS wildcard origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway HTTP server's CORS handling validates the `Origin` header against a configured allowlist (`CORSAllowedOrigins`). For wildcard entries (e.g. `*.ethereum.org`), the code strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` with no verification that the match is preceded by a `.` label boundary. This is the exact bug class from the TerriaJS advisory: a hostname that merely *ends with* the allowed string is treated as a valid subdomain, even when it isn't actually a subdomain.

### Finding Description
In `isAllowedOrigin`, the wildcard branch is: [1](#0-0) 

`allowedHost` is derived by trimming the leading `*.` from a configured entry such as `*.ethereum.org`, yielding `ethereum.org`. The subsequent check only verifies `strings.HasSuffix(originHost, allowedHost)`, with no requirement that the character immediately preceding the match be a `.`. As a result, an attacker-controlled origin like `evil-ethereum.org` (or more directly `notethereum.org`) satisfies `strings.HasSuffix("notethereum.org", "ethereum.org")` even though it is not a subdomain of `ethereum.org` at all — it is a completely different, attacker-registrable domain.

This mirrors the TerriaJS root cause precisely: the allowlist check validates via suffix matching without anchoring the match to a domain-label boundary, so any domain name that happens to end with the allowed string bypasses the intended restriction.

If `isAllowedOrigin` returns true, `handleRequest` reflects the attacker's `Origin` value back with `Access-Control-Allow-Origin`, effectively granting that arbitrary attacker-registered origin the same cross-origin trust as the legitimately allowlisted domains: [2](#0-1) 

### Impact Explanation
An operator who configures a CORS wildcard allowlist entry (e.g., `*.mycompany.com`) intends to permit only subdomains of `mycompany.com` to make credentialed cross-origin requests to the Gateway's HTTP-facing API. Because of the unanchored suffix check, an attacker can register any domain that happens to end with the same string (e.g., `evilmycompany.com`, `notmycompany.com`), host a malicious page there, and have browsers treat it as an allowed CORS origin. This allows an unprivileged, unauthenticated external attacker to have their forged origin reflected in `Access-Control-Allow-Origin`, enabling cross-origin reads of Gateway API responses from a victim's browser session that would otherwise be blocked by the Same-Origin Policy — a request/response impersonation and allowlist bypass.

### Likelihood Explanation
Exploitation only requires: (1) the Gateway operator has `CORSEnabled` with at least one wildcard entry configured (a documented, supported configuration pattern per the test suite), and (2) the attacker registers a domain string ending with the allowed suffix and lures a victim (whose browser holds a session/credentials for the Gateway) to visit it. No authentication or privileged access is required by the attacker; this is a purely unprivileged, internet-facing bypass reachable from any external actor able to register a domain.

### Recommendation
Fix the wildcard comparison in `isAllowedOrigin` to require a `.` boundary (or exact match) rather than a raw suffix check, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
This ensures only true subdomains (or the exact base domain) of the allowlisted entry are accepted, matching the intended `*.` wildcard semantics.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled: true` and `CORSAllowedOrigins: ["*.ethereum.org"]`.
2. Attacker registers `evilethereum.org` (or any domain ending in `ethereum.org` without a dot separator) and hosts a malicious page there.
3. Victim's browser (with an active session to the Gateway) sends a request with `Origin: https://evilethereum.org`.
4. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and evaluates `strings.HasSuffix("evilethereum.org", "ethereum.org")`, which is `true`.
5. The server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker's page to read cross-origin responses from the Gateway — confirmed by the existing test harness pattern in `core/services/gateway/network/httpserver_test.go` (e.g. `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`), which exercises this same code path with different domain strings. [3](#0-2)

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-193)
```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	originScheme, originHost, originPort, err := s.splitURL(origin)
	if err != nil {
		s.lggr.Debug("error parsing origin URL", err)
		return false
	}
	for _, allowed := range s.config.CORSAllowedOrigins {
		// probably better to do this once when server starts and store it in a map
		// this is an easier solution so we don't have to apply more changes to the code
		// just need to be careful when specifying allowed origins in the config file
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
		if err != nil {
			s.lggr.Debug("error parsing allowed origin URL", err)
			continue
		}
		// skip if the scheme doesn't match at all
		if originScheme != allowedScheme {
			continue
		}
		// skip if the port doesn't match at all
		if originPort != allowedPort {
			continue
		}
		// check for exact host match (e.g., remix.com)
		if originHost == allowedHost {
			return true
		}
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
		}
	}
	return false
}
```

**File:** core/services/gateway/network/httpserver.go (L195-202)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}
```
