The code exactly matches the claim. `isAllowedOrigin` strips `*.` and does a raw `strings.HasSuffix(originHost, allowedHost)` comparison with no label-boundary check, confirmed at [1](#0-0) . This means an origin like `evilethereum.org` would satisfy `strings.HasSuffix("evilethereum.org", "ethereum.org")` and be treated as matching a `*.ethereum.org` wildcard entry, even though it's not a genuine subdomain.

This directly feeds into `handleRequest`, which reflects the raw `Origin` header into `Access-Control-Allow-Origin` whenever `isAllowedOrigin` returns true [2](#0-1) . There's no additional check or sanitization elsewhere in this path that would prevent the bypass — the exact-match check on line 181 doesn't help since the suffix check is a separate, subsequent branch that fires independently.

This is triggerable by any unprivileged network client that can register a domain and send an HTTP request with a crafted `Origin` header — no credential, role, or special access is required. It's a genuine CORS allowlist bypass with a concrete, verifiable root cause in gateway-facing code, matching an in-scope impact category (allowlist bypass leading to cross-user response exposure via reflected CORS headers).

Audit Report

## Title
CORS wildcard-origin allowlist bypass due to unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway's `isAllowedOrigin` function implements wildcard CORS origin matching by stripping the `*.` prefix and performing a raw `strings.HasSuffix` comparison against the request's `Origin` host, without verifying a preceding `.` label separator. This allows an attacker-registered domain that merely ends with the same string (e.g., `evilethereum.org` vs. allowed `*.ethereum.org`) to be treated as a trusted subdomain and have its origin reflected in `Access-Control-Allow-Origin`.

## Finding Description
In `isAllowedOrigin`, after stripping the wildcard prefix, the code does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
There is no boundary check ensuring the character immediately preceding the matched suffix in `originHost` is a `.`. Consequently, `originHost = "evilethereum.org"` and `allowedHost = "ethereum.org"` (from configured `*.ethereum.org`) pass `strings.HasSuffix`, incorrectly granting trust. This function is called directly from `handleRequest`, which reflects the raw `Origin` header into `Access-Control-Allow-Origin` when `isAllowedOrigin` returns true, with no further validation. [3](#0-2) 

## Impact Explanation
Any gateway operator using a wildcard CORS entry (e.g., `https://*.chain.link`) unintentionally allows any attacker-registered domain ending in that literal string (e.g., `evilchain.link`) to have its origin reflected into `Access-Control-Allow-Origin`. This lets a malicious site hosted on such a domain make credentialed cross-origin requests to the gateway and have browsers permit reading the response, defeating the purpose of the CORS allowlist — a gateway request impersonation / allowlist bypass.

## Likelihood Explanation
Exploitation requires only that the operator has configured a wildcard CORS entry (a supported, documented feature) and that the attacker registers or controls a domain sharing the suffix string. Domain names are attacker-choosable, making this practically and repeatably exploitable wherever wildcard CORS entries are configured — no special privilege or credential is needed.

## Recommendation
Anchor the wildcard match to a domain-label boundary, e.g., require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of the raw `strings.HasSuffix` check.

## Proof of Concept
1. Start the gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a POST request to the server with header `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, confirming `isAllowedOrigin` incorrectly matched a non-subdomain. This can be encoded as a Go unit test analogous to the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` in `httpserver_test.go`, but using `origin := "https://evilethereum.org"` (which ends with `ethereum.org` but is not a subdomain) and asserting that `Access-Control-Allow-Origin` is set (demonstrating the bypass) rather than empty.

### Citations

**File:** core/services/gateway/network/httpserver.go (L184-202)
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
}

func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}
```
