The code confirms the claim exactly as described. This requires operator configuration (`CORSEnabled=true` with a wildcard entry in `CORSAllowedOrigins`), but that is a documented, supported configuration option — not a misconfiguration outside the code's design, since the wildcard syntax `*.` is explicitly supported by the code itself. Given a wildcard is configured, the bypass is real and requires no special credentials from the attacker.

Audit Report

## Title
CORS Origin Allowlist Bypass via Improper Suffix Matching in Gateway HTTP Server - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements wildcard CORS matching (e.g. `*.remix.com`) by stripping the `*.` prefix and calling `strings.HasSuffix(originHost, allowedHost)`, without verifying a `.` domain-label boundary precedes the match. This allows an attacker-controlled domain like `evilremix.com` to satisfy the suffix check against an allowlisted `remix.com` pattern, even though it is not a legitimate subdomain.

## Finding Description
The vulnerable logic is: [1](#0-0) 

This is reached directly from `handleRequest`, which reads the attacker-controlled `Origin` header and reflects it back in `Access-Control-Allow-Origin` when `isAllowedOrigin` returns true: [2](#0-1) 

There is no check that the character preceding the matched suffix is a `.`, so `strings.HasSuffix("evilremix.com", "remix.com")` returns `true` for an attacker's own unrelated domain, and no other middleware in this file (scheme/port equality checks at [3](#0-2)  ) compensates for this — those checks only validate scheme and port, not the host boundary.

## Impact Explanation
When an operator configures a wildcard entry in `CORSAllowedOrigins` (a supported, documented pattern per the code comment `// check for wildcard host match (e.g., *.remix.com)`), an unauthenticated attacker who registers a suffix-colliding domain can have their origin treated as trusted, causing the Gateway to set `Access-Control-Allow-Origin` to the attacker's origin and allow browser-based cross-origin access to the user-facing Gateway API intended to be restricted to legitimate subdomains. This matches the in-scope "allowlist bypass / cross-user response corruption" impact class for the Gateway's internet-facing HTTP server.

## Likelihood Explanation
Exploitation only requires: (1) the operator having configured `CORSEnabled=true` with at least one wildcard entry in `CORSAllowedOrigins` — a legitimate, code-supported configuration rather than a misconfiguration — and (2) the attacker registering any domain ending in the allowlisted suffix and sending a request with a crafted `Origin` header, which is well within normal unprivileged client capability against an internet-facing endpoint.

## Recommendation
Fix the wildcard comparison to require an actual subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```

## Proof of Concept
1. Configure `HTTPServerConfig{CORSEnabled: true, CORSAllowedOrigins: []string{"https://*.remix.com"}}` and start the Gateway HTTP server.
2. Send `GET /` (or the configured `Path`) to the server with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`, confirming `isAllowedOrigin` incorrectly returned `true` for a non-subdomain suffix match — verifiable via a Go unit test directly calling `httpServer.isAllowedOrigin("https://evilremix.com")` after constructing the server with the above config.

### Citations

**File:** core/services/gateway/network/httpserver.go (L172-183)
```go
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
```

**File:** core/services/gateway/network/httpserver.go (L184-190)
```go
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
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
