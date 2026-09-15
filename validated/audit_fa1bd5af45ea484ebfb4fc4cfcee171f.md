Audit Report

## Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - ([File: core/services/gateway/network/httpserver.go])

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements wildcard CORS origin matching using `strings.HasSuffix` without anchoring the match to a `.`-delimited label boundary. As a result, an attacker-controlled hostname that merely ends with the configured allowed suffix (e.g., `evilethereum.org` vs. allowed `*.ethereum.org`) is incorrectly treated as an allowed subdomain, letting an unrelated origin be reflected into `Access-Control-Allow-Origin`.

## Finding Description
The wildcard-matching branch of `isAllowedOrigin` strips the `*.` prefix from the configured allowlist entry and then does a raw suffix comparison: [1](#0-0) 
Because `strings.HasSuffix` is a pure substring-suffix check, it has no notion of domain-label boundaries: `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates to `true` even though `evilethereum.org` is not a subdomain of `ethereum.org` at all — it is an entirely different registrable domain that happens to share a character suffix. The correct check should require that `originHost` equal `allowedHost` or end with `"."+allowedHost`.

This function is called directly from the request path with no other mitigating check: [2](#0-1) 
`origin` comes straight from the client-controlled `Origin` header of an unprivileged HTTP request; there is no additional validation of the origin format elsewhere, and the scheme/port equality checks preceding the wildcard branch do not constrain the hostname boundary issue: [3](#0-2) 

The existing test suite only checks a negative case where the suffix genuinely does not match (`ethereum.remix.org` vs `ethereum.org`), and does not cover the boundary-less concatenation case, so the bug is untested and unfixed in the current code.

## Impact Explanation
When an operator configures `CORSAllowedOrigins` with a wildcard entry such as `https://*.ethereum.org`, they intend to trust only genuine subdomains of `ethereum.org`. Due to the missing label-boundary anchor, any attacker who can register/host a domain whose name merely ends with that string (e.g., `evilethereum.org`) is granted the same trust — their origin gets reflected into `Access-Control-Allow-Origin`, permitting their browser-hosted page to read cross-origin gateway responses. This is a concrete allowlist bypass on the gateway's internet-facing HTTP endpoint (`handleRequest`), falling under the in-scope "allowlist bypass" / cross-user response exposure impact category.

## Likelihood Explanation
Exploitation requires only that the operator has enabled a wildcard CORS entry (a documented, supported configuration feature, not a misconfiguration outside intended use) and that the attacker registers/hosts a domain with the matching suffix — no privileged access, credentials, or victim social engineering beyond normal browsing to the attacker's site is needed. This matches an unprivileged, remotely triggerable bypass.

## Recommendation
Anchor the wildcard suffix match to a real domain-label boundary:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
Add a regression test asserting `https://evilethereum.org` is rejected when the allowlist contains `https://*.ethereum.org`.

## Proof of Concept
1. Start the gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send an HTTP request to the gateway's request path with header `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, confirming `isAllowedOrigin` returns `true` via `strings.HasSuffix("evilethereum.org", "ethereum.org")`.
4. This can be captured as a Go unit test analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` in `core/services/gateway/network/httpserver_test.go`, but asserting the opposite (that the header IS set) for origin `https://evilethereum.org` against allowlist `https://*.ethereum.org`, proving the bypass.

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
