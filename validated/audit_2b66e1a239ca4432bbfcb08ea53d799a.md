Confirmed — the code exactly matches the claim. `isAllowedOrigin` at line 187 performs `strings.HasSuffix(originHost, allowedHost)` on the wildcard branch with no boundary check that the preceding character is a `.`. This is a real, reachable, unauthenticated bypass: an operator configuring `CORSAllowedOrigins: ["https://*.ethereum.org"]` would have `https://evilethereum.org` pass the check, causing the server to reflect `Access-Control-Allow-Origin: https://evilethereum.org` at lines 198-201, exposing gateway responses to a cross-origin attacker page. The existing test suite only exercises true subdomain matches (`remix.ethereum.org`, `another.valid.domain.com`, `example.gov`) and does not cover the boundary-omission case, confirming the gap is unexercised.

This requires only an operator to have configured a wildcard CORS entry (a documented, supported feature) and an attacker to register/control a domain with the vulnerable suffix — no operator/admin privileges are needed by the attacker, and the exploit is triggerable via a normal browser request against the internet-facing Gateway HTTP server. The root cause (missing label-boundary check on suffix match) and impact (CORS allowlist bypass leading to cross-origin disclosure of gateway responses) are concrete and map to an in-scope impact category (allowlist bypass / cross-user response corruption via CORS).

Audit Report

## Title
CORS `isAllowedOrigin` wildcard suffix match lacks a label boundary, allowing origin allowlist bypass — ([File: core/services/gateway/network/httpserver.go])

## Summary
The Gateway HTTP server's `isAllowedOrigin` function validates wildcard CORS entries (e.g. `*.domain.com`) using `strings.HasSuffix(originHost, allowedHost)` without checking that the matched suffix is preceded by a `.` label boundary. This allows an attacker-controlled origin such as `evilethereum.org` to bypass an allowlist entry of `*.ethereum.org`, since it merely ends with the same byte sequence as the trusted domain.

## Finding Description
In `core/services/gateway/network/httpserver.go`, the wildcard branch of `isAllowedOrigin` strips the `*.` prefix from the configured allowed host and then checks `strings.HasSuffix(originHost, allowedHost)` [1](#0-0) . This check validates only that `originHost` ends with the trusted substring as raw bytes, without requiring a `.` immediately before the match. As a result, `evilethereum.org` satisfies `HasSuffix("evilethereum.org", "ethereum.org")`, despite being an entirely separate, attacker-registrable domain unrelated to `ethereum.org`. The subsequent `handleRequest` handler reflects the raw `Origin` header value into `Access-Control-Allow-Origin` upon a positive match, with no further validation [2](#0-1) . The existing test suite (`TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`) only exercises legitimate subdomain matches, and does not cover the label-boundary-omission case, so this gap is not caught by CI.

## Impact Explanation
This is a CORS allowlist bypass (CWE-20/CWE-625 class, unanchored substring/suffix matching). It allows an attacker who registers a domain crafted to end with the same string as an operator's configured wildcard entry to have their origin reflected in `Access-Control-Allow-Origin`, enabling a malicious webpage to make authenticated cross-origin browser requests to the Gateway's `ProcessRequest` endpoint and read responses that should be restricted to the operator's trusted frontends. This matches an in-scope impact category of allowlist bypass / cross-origin response exposure.

## Likelihood Explanation
Exploitability requires the operator to have configured at least one wildcard `CORSAllowedOrigins` entry, which is a supported and tested configuration pattern. Given that precondition, any attacker can register a domain ending in the same byte sequence as the allowed domain (trivial and unrestricted domain registration) and host a page that triggers the cross-origin request from a victim's browser — no privileged access to the Gateway itself is required.

## Recommendation
Enforce a proper DNS label boundary for wildcard suffix comparisons: require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix(originHost, allowedHost)`.

## Proof of Concept
1. Start the Gateway HTTP server with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.ethereum.org"}`.
2. Send an HTTP request to the server with header `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` (since `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`), and the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, and `Access-Control-Allow-Headers: Content-Type` — confirming the allowlist bypass. This can be added as a unit test alongside the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` test using the same `startNewServer`/`sendRequest` helpers.

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
