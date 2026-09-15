Audit Report

## Title
CORS wildcard-origin allowlist bypass via missing domain-boundary check enables cross-origin response disclosure - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` matches wildcard CORS allowlist entries (e.g. `https://*.ethereum.org`) using a plain `strings.HasSuffix(originHost, allowedHost)` check with no domain-boundary validation. This lets any origin that merely ends with the configured suffix (e.g. `evilethereum.org`) pass as an allowed subdomain of `ethereum.org`, even though it is an unrelated domain.

## Finding Description
The code confirms the claim exactly. In `isAllowedOrigin`: [1](#0-0) 
the wildcard branch strips `*.` from the configured host and then checks only `strings.HasSuffix(originHost, allowedHost)`, with no requirement that a `.` character (or exact boundary) precede the matched suffix in `originHost`. As a result, `evilethereum.org` satisfies `HasSuffix("evilethereum.org", "ethereum.org")` and is treated as a valid subdomain of the allowlisted `*.ethereum.org` entry.

`handleRequest` then reflects the attacker-controlled `Origin` header value directly into `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true: [2](#0-1) 
No additional origin re-validation or allowlist mechanism exists downstream to catch this — the boundary check is entirely absent, and the existing test suite in `httpserver_test.go` only exercises positive matches (true subdomains) and negative cases with a *different* suffix (e.g., `ethereum.remix.org`), never a same-suffix-different-domain probe like `evilethereum.org`, so this gap is untested.

## Impact Explanation
This is the gateway's internet-facing HTTP endpoint, reachable by any unprivileged remote client with knowledge of a wildcard CORS configuration. If an operator enables CORS with a wildcard entry (a supported, documented configuration pattern), an attacker who registers or controls a domain sharing the suffix string (without a subdomain boundary) can have a browser page hosted there receive `Access-Control-Allow-Origin` reflecting their own origin, allowing their page's script to read the gateway's JSON-RPC response body via Fetch/XHR — a concrete cross-origin response disclosure that undermines the CORS allowlist's intended restriction to legitimate operator UI domains.

## Likelihood Explanation
Exploitation requires only that (1) the operator has configured a wildcard entry in `CORSAllowedOrigins` (a normal, supported usage pattern, not a misconfiguration of the underlying feature), and (2) the attacker registers a cheap look-alike domain sharing the suffix. No credentials, host access, or victim social engineering beyond luring a user to a webpage is needed, and the request itself is a standard cross-origin fetch, fully triggerable by an unprivileged client.

## Recommendation
Enforce a proper subdomain boundary in the wildcard match, e.g., require `originHost == baseDomain || strings.HasSuffix(originHost, "."+baseDomain)` instead of a bare `strings.HasSuffix` check, so `evilethereum.org` is correctly rejected while `remix.ethereum.org` is still accepted.

## Proof of Concept
1. Start the gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = []string{"https://*.ethereum.org"}` (as in `startNewServer` helper in `httpserver_test.go`).
2. Send a request with header `Origin: https://evilethereum.org` to the server's configured path.
3. Observe `isAllowedOrigin` returns `true` (since `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`), and the response includes `Access-Control-Allow-Origin: https://evilethereum.org`.
4. Add a unit test analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` asserting that origin `https://evilethereum.org` against allowlist `https://*.ethereum.org` is currently (incorrectly) accepted, confirming the missing boundary check.

### Citations

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
