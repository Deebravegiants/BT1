### Title
CORS Origin Allowlist Bypass via Improper Suffix Matching in Gateway HTTP Server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's internet-facing HTTP server validates cross-origin requests against a configured `CORSAllowedOrigins` allowlist. When a wildcard entry (e.g. `*.remix.com`) is configured, the matching logic strips the `*.` prefix and then performs a raw `strings.HasSuffix` comparison against the origin's host, without verifying that the preceding character is a domain-label boundary (`.`). This is the same bug class as the reported in-toto-golang advisory: a security-relevant string/path comparison that uses naive prefix/suffix semantics instead of proper boundary-aware matching, allowing an attacker-controlled string that merely shares a suffix (not an actual subdomain relationship) to satisfy the allowlist check.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  loops over configured allowed origins and, for wildcard entries, does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
This code strips the `*.` prefix from an allowlist entry like `*.remix.com` to get `remix.com`, then checks whether the attacker-supplied `Origin` header host ends with that string. Because there is no check that the character immediately preceding the matched suffix is a `.` (i.e., no verification that `originHost` is actually a proper subdomain of `allowedHost` rather than an unrelated domain that happens to share a trailing substring), an origin such as `evilremix.com` or `notremix.com` satisfies `strings.HasSuffix("evilremix.com", "remix.com")` and is treated as an allowed origin even though it has no relationship to the legitimate `remix.com` domain.

This function is invoked directly from `handleRequest` at [2](#0-1)  using the attacker-controlled `Origin` request header, and on success sets `Access-Control-Allow-Origin` to the attacker's own origin value, unconditionally granting CORS access to the Gateway's user-facing API for any client presenting a crafted Origin header — no authentication or prior trust relationship required.

### Impact Explanation
An unprivileged, unauthenticated remote attacker can register a domain that merely shares a trailing substring with an operator's intended trusted subdomain pattern (e.g., `evil-remix.com` vs. allowlisted `*.remix.com`) and have their origin accepted by the Gateway's CORS policy. This bypasses the allowlist/isolation control the operator configured, enabling cross-origin browser clients hosted on the attacker's domain to interact with the Gateway's user-facing HTTP endpoint as if they were a trusted origin, exposing responses/session data to a domain the operator never intended to trust. This maps to the "allowlist bypass" / "cross-user response confusion" class explicitly called out as in-scope.

### Likelihood Explanation
Likelihood is moderate-to-high: exploitation only requires registering an attacker-controlled domain whose name ends with the allowlisted suffix (a trivial DNS registration, no privileged access to Chainlink infrastructure needed) and sending a normal HTTP request with a crafted `Origin` header — a routine unprivileged client action against the internet-facing gateway HTTP server. It requires that the operator has configured at least one wildcard entry in `CORSAllowedOrigins`, which is a documented/supported configuration option.

### Recommendation
Fix the wildcard host comparison in `isAllowedOrigin` to require a proper subdomain boundary, e.g. check that `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix`, mirroring how the in-toto-golang fix required exact path-segment boundaries rather than raw substring/prefix matching.

### Proof of Concept
1. Operator configures `CORSAllowedOrigins = ["*.remix.com"]` on the Gateway user-facing HTTP server (`HTTPServerConfig.CORSAllowedOrigins`).
2. Attacker registers `evilremix.com` (or any domain ending in `remix.com`, e.g. `notremix.com`) and serves a web page from it.
3. Attacker's browser sends a request to the Gateway endpoint with header `Origin: https://evilremix.com`.
4. In `isAllowedOrigin`, `allowedHost` becomes `remix.com` after stripping `*.`, and `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`, so the function returns `true`.
5. `handleRequest` sets `Access-Control-Allow-Origin: https://evilremix.com`, granting the untrusted origin CORS access to the Gateway API that was intended to be restricted to legitimate `*.remix.com` subdomains. [3](#0-2)

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-209)
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

func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}
```
