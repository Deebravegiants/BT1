The code confirms the claim exactly as described. The vulnerable logic is real and unmodified.

Audit Report

## Title
CORS Origin Allowlist Bypass via Improper Suffix Matching in Gateway HTTP Server - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` strips the `*.` prefix from a wildcard-configured allowed origin (e.g. `*.remix.com` → `remix.com`) and then checks the request's `Origin` header host with a bare `strings.HasSuffix`, without validating a `.`-boundary before the matched suffix. This allows any attacker-controlled domain that merely ends with the allowlisted string (e.g. `evilremix.com`) to be treated as a trusted origin.

## Finding Description
In `isAllowedOrigin` [1](#0-0) , when an allowlist entry has the `*.` wildcard prefix, the code does `allowedHost = allowedHost[2:]` then `strings.HasSuffix(originHost, allowedHost)`. This is a naive substring/suffix check rather than a subdomain-boundary check: `strings.HasSuffix("evilremix.com", "remix.com")` returns `true` even though `evilremix.com` is not a subdomain of `remix.com`. The exact host match branch above it [2](#0-1)  is unaffected but does not mitigate the wildcard branch's flaw.

This function is called directly from `handleRequest` using the unauthenticated, attacker-controlled `Origin` header [3](#0-2) . On a match, the server reflects the attacker's own origin value back in `Access-Control-Allow-Origin`, granting that origin CORS access to the gateway's HTTP endpoint. No authentication, credential, or prior trust relationship is required — this is reachable by any unprivileged network client sending a normal HTTP request with a crafted `Origin` header, and it's only exploitable when the operator has configured at least one wildcard entry in `CORSAllowedOrigins`, which is a documented/supported configuration option [4](#0-3) .

## Impact Explanation
This is a legitimate CORS allowlist bypass: an operator who intends to trust only `*.remix.com` subdomains inadvertently also trusts any domain sharing that trailing substring (`evilremix.com`, `notremix.com`, etc.). A browser-based attacker hosted on such a domain can have `Access-Control-Allow-Origin` reflect their origin and read cross-origin responses from the gateway's user-facing API that were meant to be restricted to legitimate subdomains, falling into the "allowlist bypass" / "cross-user response confusion" impact class.

## Likelihood Explanation
Exploitation requires only registering an inexpensive domain name ending in the allowlisted suffix and sending a request with a forged `Origin` header — no privileged access, credentials, or host access needed. It is gated on the operator configuring a wildcard entry in `CORSAllowedOrigins`, which is a supported and plausible configuration, not a misconfiguration outside the code's intended usage.

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
1. Configure `HTTPServerConfig.CORSAllowedOrigins = []string{"*.remix.com"}` and `CORSEnabled = true` on the gateway's user-facing HTTP server.
2. Send an HTTP request to the gateway's configured `Path` with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`, confirming `isAllowedOrigin` incorrectly returned `true` for a non-subdomain origin.
4. A Go unit test calling `httpServer.isAllowedOrigin("https://evilremix.com")` with `CORSAllowedOrigins: []string{"*.remix.com"}` configured would assert `true`, demonstrating the bypass (expected/correct behavior is `false`).

### Citations

**File:** core/services/gateway/network/httpserver.go (L53-54)
```go
	CORSEnabled            bool
	CORSAllowedOrigins     []string
```

**File:** core/services/gateway/network/httpserver.go (L180-183)
```go
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
