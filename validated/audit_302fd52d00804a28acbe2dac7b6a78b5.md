Audit Report

## Title
Overly Permissive CORS Wildcard-Origin Matching via Improper Domain-Suffix Check - ([File: core/services/gateway/network/httpserver.go])

## Summary
The Gateway HTTP server's `isAllowedOrigin` function validates wildcard CORS entries (e.g. `*.ethereum.org`) using a raw `strings.HasSuffix` comparison without enforcing a `.` boundary before the matched suffix. This allows any origin host that merely *ends with* the allowed domain string — such as `evil-ethereum.org` for an allowlist entry of `*.ethereum.org` — to be treated as a valid subdomain and granted `Access-Control-Allow-Origin`.

## Finding Description
In `isAllowedOrigin`, when an allowlist entry starts with `*.`, the code strips the prefix and then checks: [1](#0-0) 
`strings.HasSuffix(originHost, allowedHost)` has no boundary check, so `HasSuffix("evil-ethereum.org", "ethereum.org")` returns `true` even though `evil-ethereum.org` is not a subdomain of `ethereum.org` at all — it's an entirely distinct, attacker-registerable domain. This function is invoked for every request in `handleRequest`, which reflects the raw `Origin` header value back in `Access-Control-Allow-Origin` when `isAllowedOrigin` returns true: [2](#0-1) 
No other validation layer (auth middleware, role check, or additional origin normalization) intervenes before this reflection occurs. The wildcard-origin feature is a real, supported, documented configuration option, confirmed by sample configs (`core/scripts/gateway/sample_config.toml`, `sample_config_tls.toml`) and by dedicated test coverage (`TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` in `core/services/gateway/network/httpserver_test.go`), rather than an edge case introduced solely by operator error.

## Impact Explanation
This maps to the in-scope "gateway request impersonation / allowlist bypass" category. If an operator uses a wildcard `CORSAllowedOrigins` entry — a documented and tested pattern — an attacker who registers a lookalike domain sharing the literal suffix (e.g. `evil-ethereum.org` vs. `*.ethereum.org`) can have their site's origin reflected in `Access-Control-Allow-Origin`. A victim browsing to the attacker's page would then have their browser permit cross-origin `fetch`/XHR reads of gateway JSON-RPC responses intended only for genuine subdomains of the allowed domain, enabling cross-user response disclosure via CORS bypass.

## Likelihood Explanation
Exploitation only requires (1) an operator using a wildcard entry in `CORSAllowedOrigins` — a normal, supported configuration, not a misconfiguration — and (2) an attacker registering a cheap, unrelated domain sharing the suffix string. No privileged access, credentials, or host access is needed by the attacker; the flawed comparison is purely a logic bug in code reachable by any unprivileged HTTP client via the `Origin` header, matching the classic domain-suffix-matching CORS bug class (e.g., CVE-2017-14460).

## Recommendation
Enforce a `.` boundary (or exact match) when checking wildcard suffixes:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```

## Proof of Concept
1. Configure the gateway user server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send an HTTP POST request to the gateway's user-facing endpoint with header `Origin: https://evil-ethereum.org`.
3. Observe `isAllowedOrigin` returns `true` (via `strings.HasSuffix("evil-ethereum.org", "ethereum.org")`), and the response includes `Access-Control-Allow-Origin: https://evil-ethereum.org` as set in `handleRequest` (core/services/gateway/network/httpserver.go, lines 195-202).
4. This can be directly demonstrated by adding a test case analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` in `core/services/gateway/network/httpserver_test.go`, but using origin `https://evil-ethereum.org` against allowlist `https://*.ethereum.org`, and asserting the response incorrectly grants CORS access.

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
