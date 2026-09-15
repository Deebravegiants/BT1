This is a confirmed, real bug — the code matches the claim exactly.The vulnerability is confirmed by direct code inspection — no boundary check exists in the wildcard suffix match.

Audit Report

## Title
CORS wildcard-origin allowlist bypass via missing domain-boundary check in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

## Summary
The Gateway's `isAllowedOrigin` function implements wildcard CORS origin matching (e.g. `https://*.chain.link`) using a raw `strings.HasSuffix` comparison with no domain-boundary enforcement. Any attacker-registered domain whose name merely ends with the configured suffix string (e.g. `evilchain.link` matching a `*.chain.link` allowlist entry) is incorrectly treated as an allowed origin, letting an unrelated attacker-controlled site pass the CORS check.

## Finding Description
`isAllowedOrigin` splits the request `Origin` header and each configured allowed origin into scheme/host/port via `splitURL`, then for entries prefixed with `*.` strips that prefix and checks `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

`HasSuffix` is a pure string-suffix comparison — it does not require that `originHost` be a subdomain of `allowedHost` (i.e., it doesn't check for a preceding `.` or exact equality). Given `CORSAllowedOrigins = ["https://*.chain.link"]`, `allowedHost` becomes `chain.link`. An attacker's origin `https://evilchain.link` produces `originHost = "evilchain.link"`, and `strings.HasSuffix("evilchain.link", "chain.link")` returns `true`, incorrectly matching.

This function is invoked directly in `handleRequest`, the entry point for every unprivileged request to the Gateway's public HTTP endpoint, using the fully attacker-controlled `Origin` header: [2](#0-1) 

If the check passes, the attacker's `Origin` is reflected verbatim into `Access-Control-Allow-Origin`, granting that unrelated origin cross-origin trust. No existing validation elsewhere corrects this boundary check — the exact-match branch (`originHost == allowedHost`) is a separate `if` and does not gate the wildcard branch.

## Impact Explanation
This is a genuine allowlist-bypass bug in a code path reachable by any unprivileged HTTP client that controls the `Origin` header, which maps to the "allowlist bypass" impact category for the Gateway's CORS policy. Exploitation only yields value when combined with credentialed/session-bearing cross-origin traffic against Gateway endpoints, but the root-cause defect itself — treating `evilchain.link` as a subdomain of `chain.link` — is real and directly attributable to this code, not to any operator misconfiguration (using wildcard entries is a supported, documented feature, and the bug is in how the wildcard is matched, not in the act of configuring one).

## Likelihood Explanation
Exploitation requires only that the operator has configured at least one wildcard entry in `CORSAllowedOrigins`, a supported and documented configuration option, and that the attacker registers a domain name ending in the same character sequence as the configured suffix (an inexpensive, easily achievable step). No special network position, privileged credentials, or victim interaction beyond the attacker's own domain registration is required to satisfy the check purely via the `Origin` header on a normal request.

## Recommendation
Enforce a proper domain boundary in the wildcard branch of `isAllowedOrigin`: instead of `strings.HasSuffix(originHost, allowedHost)`, require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`, so that `evilchain.link` is correctly rejected as not matching `*.chain.link`.

## Proof of Concept
1. Start the Gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.chain.link"]`.
2. Send a request with header `Origin: https://evilchain.link`.
3. Observe `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilchain.link", "chain.link")` is `true`.
4. Observe the response includes `Access-Control-Allow-Origin: https://evilchain.link`.
5. A Go unit test analogous to the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` in `core/services/gateway/network/httpserver_test.go`, but asserting a request from `https://evilchain.link` against `CORSAllowedOrigins = ["https://*.chain.link"]` is rejected, will fail on current code, demonstrating the bypass.

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
