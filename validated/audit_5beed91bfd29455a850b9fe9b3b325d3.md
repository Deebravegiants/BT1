The code exactly matches the claim: `isAllowedOrigin` at [1](#0-0)  strips the `*.` prefix and performs a plain `strings.HasSuffix(originHost, allowedHost)` check with no boundary/dot verification, meaning `originHost = "evilethereum.org"` satisfies suffix `"ethereum.org"` while not being an actual subdomain.

This flows directly into CORS header setting in `handleRequest` at [2](#0-1) , which echoes the attacker-controlled `Origin` header value into `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true. The existing test suite only validates true subdomains and scheme/port mismatches, confirmed by `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` and `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards`, neither of which exercises a suffix-collision non-subdomain host like `evilethereum.org` against `*.ethereum.org`.

This is a genuine, reachable, code-level logic bug: it requires no special privilege beyond being able to send a browser/HTTP request with a crafted `Origin` header — well within an unprivileged external client's capability — and the only precondition is that the operator has configured a wildcard CORS entry, which is a supported, documented configuration option (not a misconfiguration outside intended use, since wildcard support itself is a legitimate designed feature whose enforcement is broken). The impact — CORS bypass permitting an attacker-registered domain to receive `Access-Control-Allow-Origin` grants for the gateway's user-facing JSON-RPC endpoint — maps to the in-scope "gateway request impersonation / cross-user response corruption via allowlist bypass" category.

Audit Report

## Title
CORS wildcard origin allowlist bypass via missing subdomain boundary check - (File: core/services/gateway/network/httpserver.go)

## Summary
The Gateway's `isAllowedOrigin` function in `core/services/gateway/network/httpserver.go` implements wildcard CORS matching (`*.example.com`) using a bare `strings.HasSuffix` check on the origin host, without requiring a `.` boundary before the matched suffix. This allows an attacker-controlled domain that merely ends with the allowed suffix string (e.g., `evilethereum.org` vs. allowed `*.ethereum.org`) — but is not an actual subdomain — to pass the CORS check and receive a reflected `Access-Control-Allow-Origin` header.

## Finding Description
In `isAllowedOrigin` (`core/services/gateway/network/httpserver.go:184-190`), once the `*.` prefix is stripped from the configured allowed host, the remaining suffix comparison is:
```go
if strings.HasSuffix(originHost, allowedHost) {
    return true
}
```
This lacks a check that the character preceding the matched suffix in `originHost` is a `.` (or that `originHost` equals `allowedHost` exactly). Consequently, hosts like `evilethereum.org`, `notethereum.org`, or `xethereum.org` all satisfy `strings.HasSuffix(originHost, "ethereum.org")` despite not being subdomains of `ethereum.org`.

`handleRequest` (`core/services/gateway/network/httpserver.go:195-202`) uses this boolean directly to reflect the raw `Origin` request header value into the `Access-Control-Allow-Origin` response header, with no additional validation layer downstream. The existing regression tests (`TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` and `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards`) do not cover the suffix-collision-without-dot case, so this bypass is unguarded by tests.

## Impact Explanation
When an operator enables wildcard CORS (a supported configuration option, e.g. `CORSAllowedOrigins = ["https://*.mycompany.com"]`), an attacker who registers or controls any domain ending in that literal suffix (e.g. `evilmycompany.com`) can have browser-based cross-origin requests from that domain accepted by the gateway, with the response reflecting `Access-Control-Allow-Origin: https://evilmycompany.com`. This permits unauthorized cross-origin access to the gateway's user-facing JSON-RPC endpoint from a domain that was never intended to be trusted, enabling data exfiltration of responses and forged requests against the gateway — a gateway request impersonation / allowlist bypass class issue.

## Likelihood Explanation
Exploitation only requires: (1) the operator having configured a wildcard CORS entry, a documented and supported pattern, and (2) the attacker registering a low-cost domain name ending in the same character sequence as the allowed suffix (no dot needed) and getting a victim's browser to visit an attacker-hosted page that issues cross-origin requests to the gateway. Both preconditions are realistic and cheap to satisfy for any deployment using wildcard CORS.

## Recommendation
Enforce an explicit domain boundary in the wildcard match:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
Add regression tests for suffix-collision hosts (e.g. `evilethereum.org` against `*.ethereum.org`) to prevent regressions.

## Proof of Concept
1. Configure `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]` on the gateway's `UserServerConfig`.
2. Send an HTTP request to the gateway's user endpoint with header `Origin: https://evilethereum.org`.
3. Observe `isAllowedOrigin` returns `true` (since `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`), and the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, despite `evilethereum.org` not being a subdomain of `ethereum.org`. [1](#0-0) [2](#0-1)

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
