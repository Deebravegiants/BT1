The code exactly matches the claim. `isAllowedOrigin` strips the `*.` prefix and uses a bare `strings.HasSuffix` check without verifying a `.` label boundary precedes the match, so a domain like `evilethereum.org` would satisfy a `*.ethereum.org` allowlist entry. This is confirmed to be present, unfixed, and reachable by any unauthenticated client via the `Origin` header on the internet-facing gateway HTTP server, with the accepted origin echoed back into `Access-Control-Allow-Origin`. [1](#0-0) [2](#0-1) 

Audit Report

## Title
CORS wildcard-origin check uses unanchored suffix match, allowing origin spoofing via lookalike domains - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway's `httpServer.isAllowedOrigin` implements wildcard CORS-origin matching (`*.example.com`) by stripping the `*.` prefix and checking `strings.HasSuffix(originHost, allowedHost)`, with no verification that the preceding character is a `.` label separator. Any hostname merely ending with the configured suffix — including unrelated domains like `evilethereum.org` for a `*.ethereum.org` allowlist — is treated as an allowed CORS origin.

## Finding Description
`isAllowedOrigin` parses the incoming `Origin` header and each configured `CORSAllowedOrigins` entry via `splitURL`, then compares scheme, port, and host. For wildcard entries, after stripping the `*.` prefix, it performs a bare `strings.HasSuffix(originHost, allowedHost)` check with no boundary validation. Consequently `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, so `https://evilethereum.org` is accepted as matching allowlist entry `https://*.ethereum.org`, despite not being a subdomain. `handleRequest` calls this function and, on a match, echoes the attacker-supplied `Origin` back in `Access-Control-Allow-Origin`, allowing the browser to permit cross-origin reads of gateway responses from the spoofed origin. Existing tests only cover cases where the suffix relationship doesn't literally hold (e.g., `ethereum.remix.org` vs `*.ethereum.org`), so this specific unanchored-suffix boundary bug is not caught by the test matrix.

## Impact Explanation
The gateway is an internet-facing component brokering unprivileged client requests into the DON. If `CORSEnabled` is true and any allowlist entry uses the `*.` wildcard form, an attacker who registers a domain merely ending with the configured suffix (no subdomain relationship required, e.g. `evilethereum.org`) can serve a malicious webpage that issues cross-origin browser requests to the gateway and read the JSON-RPC responses via the spoofed `Access-Control-Allow-Origin` header — a cross-origin response confusion / access-control bypass, mapping to the in-scope "gateway request impersonation / allowlist bypass" impact class.

## Likelihood Explanation
Exploitability requires only that the operator enables `CORSEnabled=true` with a wildcard entry in `CORSAllowedOrigins` (a supported, documented configuration option, not a misconfiguration) and that the attacker registers a cheap, easily obtainable domain sharing the suffix. No privileged access, credentials, or special network position is needed — a normal unauthenticated web client triggers it purely via the `Origin` header, and the exploit is fully repeatable.

## Recommendation
Require the label boundary when doing suffix matching: after stripping `*.`, check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `HasSuffix`.

## Proof of Concept
1. Configure gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers `evilethereum.org` and serves a page there.
3. Browser on that page sends `fetch(gatewayURL, {headers: {Origin: "https://evilethereum.org"}})`.
4. `isAllowedOrigin("https://evilethereum.org")` strips wildcard to `ethereum.org`; `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`; the gateway responds with `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker page read the gateway's response cross-origin. This can be validated with a Go unit test analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` in `httpserver_test.go`, but using origin `https://evilethereum.org` against allowlist `https://*.ethereum.org` and asserting the response incorrectly contains `Access-Control-Allow-Origin`.

### Citations

**File:** core/services/gateway/network/httpserver.go (L184-192)
```go
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
		}
	}
	return false
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
