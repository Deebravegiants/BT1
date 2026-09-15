This code exactly matches the claim, and I have enough context to make a determination.

The `isAllowedOrigin` function's wildcard matching at core/services/gateway/network/httpserver.go:184-190 uses `strings.HasSuffix(originHost, allowedHost)` after stripping `*.` prefix, with no check that the character preceding the matched suffix is a `.`. This means `evilethereum.org` passes `strings.HasSuffix("evilethereum.org", "ethereum.org")` even though it is not a subdomain of `ethereum.org`. This is directly invoked from `handleRequest` at line 198, which reflects the attacker's `Origin` back in `Access-Control-Allow-Origin` on match, exposing JSON-RPC response bodies cross-origin. [1](#0-0) [2](#0-1) 

This requires the operator to opt into `CORSEnabled = true` with a wildcard entry in `CORSAllowedOrigins` — a documented, supported configuration (as shown in the test suite) rather than an operator error/misconfiguration; the vulnerability is in the matching implementation itself, not in how the feature is used. Given wildcard subdomain configuration is a supported feature and the exploit requires only registering an unrelated domain and crafting a browser-based cross-origin request — no privileged access, credentials, or host access — the bug is reachable by an unprivileged attacker and matches the "allowlist bypass" / "cross-user response corruption" impact category referenced in the rules. The claim's code citations are accurate and the described exploit flow (attacker origin `evilethereum.org` passing suffix check for `*.ethereum.org`) is verified against the literal code logic.

Audit Report

## Title
CORS Wildcard-Suffix Bypass in Gateway User HTTP Server Allows Cross-Origin Data Theft - (File: core/services/gateway/network/httpserver.go)

## Summary
The Chainlink Gateway's internet-facing user HTTP server implements a custom CORS origin allowlist check, `isAllowedOrigin`, that matches wildcard hosts (`*.host`) using a plain string-suffix comparison (`strings.HasSuffix`) with no enforcement of a subdomain boundary (i.e., no requirement that the character preceding the matched suffix be a `.`). This allows an attacker who registers a domain that merely ends with the same string (e.g., `evilethereum.org` for an allowlisted `*.ethereum.org`) to be treated as an allowed origin, enabling cross-origin reads of gateway JSON-RPC responses.

## Finding Description
In `isAllowedOrigin`, when an allowed origin has a wildcard host (`*.host`), the code strips the `*.` prefix and checks `strings.HasSuffix(originHost, allowedHost)` (core/services/gateway/network/httpserver.go:184-190). This is a naive suffix match: `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, even though `evilethereum.org` is a completely distinct, attacker-registrable domain, not a subdomain of `ethereum.org`.

This function is invoked directly in `handleRequest` (core/services/gateway/network/httpserver.go:195-202): when `CORSEnabled` is true and `isAllowedOrigin` returns true, the server reflects the request's `Origin` header into `Access-Control-Allow-Origin`, permitting the browser to expose the response body to script on the attacker's origin. No other validation exists to catch this boundary condition — the existing test suite (`httpserver_test.go`) validates correct wildcard matches and correct suffix mismatches (e.g., `ethereum.remix.org` fails) but does not test a suffix-matching-but-non-subdomain case like `evilethereum.org`.

## Impact Explanation
The gateway user HTTP server is the internet-facing entry point for unprivileged clients submitting JSON-RPC requests processed via `gateway.ProcessRequest`, whose responses can carry job/workflow results. When an operator enables CORS with a wildcard subdomain entry (a documented, supported configuration pattern, not user error), the flawed matcher allows any attacker who registers a suffix-colliding domain to read cross-origin responses that should only be visible to legitimate subdomains — an allowlist bypass enabling cross-origin data exfiltration.

## Likelihood Explanation
Exploitation requires only: (1) the gateway operator using `CORSEnabled = true` with a wildcard entry in `CORSAllowedOrigins` (a legitimate, documented, tested configuration), and (2) the attacker registering an inexpensive domain that lexically ends with the configured suffix (e.g., `evilethereum.org`). No credentials, privileged roles, or host access are required — only a browser-based fetch with a crafted `Origin` header from a domain the attacker controls.

## Recommendation
Fix `isAllowedOrigin` to require a proper subdomain boundary: the origin host must equal `allowedHost` or end with `"." + allowedHost`, not merely share a suffix. Add regression tests for suffix-colliding but non-subdomain hosts (e.g., `evilethereum.org` vs `*.ethereum.org`). Consider replacing the hand-rolled matcher with a vetted CORS library or explicit label-based host comparison.

## Proof of Concept
1. Configure: `CORSEnabled = true`, `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From attacker-controlled `https://evilethereum.org`, send: `fetch("https://<gateway-host>/user", {method:"POST", headers:{"Content-Type":"application/jsonrpc"}, body: JSON.stringify({jsonrpc:"2.0", id:"1", method:"<service>.<method>", params:{}})})`.
3. Since `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`, the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, and the browser exposes the response to the attacker's script. A Go unit test extending `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` in `httpserver_test.go` with origin `https://evilethereum.org` against `CORSAllowedOrigins = []string{"https://*.ethereum.org"}` would demonstrate `resp.Header.Get("Access-Control-Allow-Origin")` incorrectly equals the attacker origin.

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
