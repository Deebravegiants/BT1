Audit Report

## Title
CORS wildcard origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` compares the `Origin` header host against wildcard CORS allowlist entries using an unanchored `strings.HasSuffix` check, without verifying a `.` label boundary. This lets an attacker who registers any domain that merely ends with the allowed suffix (e.g., `evilethereum.org` against an allowlist entry `*.ethereum.org`) be reflected as a trusted `Access-Control-Allow-Origin`.

## Finding Description
In `isAllowedOrigin`, the wildcard match strips the `*.` prefix from the configured entry and then checks:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [1](#0-0) 

There is no check that the character immediately preceding the matched suffix is a `.`, so `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true` even though `evilethereum.org` is an entirely different, attacker-registrable domain, not a subdomain of `ethereum.org`. `handleRequest` then reflects the raw attacker-controlled `Origin` value into `Access-Control-Allow-Origin`:
```go
if s.isAllowedOrigin(origin) {
    w.Header().Set("Access-Control-Allow-Origin", origin)
    ...
}
``` [2](#0-1) 

No other check (scheme/port match, exact-host match) mitigates this, since the wildcard branch is reached only after those checks already pass and is specifically the path meant to authorize subdomains. [3](#0-2) 

## Impact Explanation
This is a genuine logic bug in the code (not a misconfiguration): an operator using the documented `*.domain` wildcard feature as intended still gets a broader allowlist than configured, because the matching function itself is unanchored. If exploited, an attacker-registered domain gets `Access-Control-Allow-Origin` reflected back, enabling cross-origin reads of Gateway API responses from a browser session that holds credentials for the Gateway — a legitimate CORS/allowlist-bypass class of impact matching "gateway request impersonation / allowlist bypass" in the target impact categories.

## Likelihood Explanation
The reachable path is: operator configures `CORSEnabled: true` with a wildcard entry like `*.ethereum.org` (a normal, documented usage), and an external attacker sends a crafted `Origin` header (or hosts a page on a domain ending in the same suffix) to trigger the flawed check — no operator/admin privileges are required by the attacker, only that the operator has enabled a wildcard CORS entry, which is a standard supported configuration, not a misuse. The victim's browser needs to actually visit an attacker page and have an active session with the gateway for the read-impact to materialize, which is a realistic, not far-fetched, precondition for CORS-based attacks generally.

## Recommendation
Anchor the wildcard suffix match to a label boundary:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
This ensures only exact matches or genuine subdomains of the allowlisted base domain are accepted.

## Proof of Concept
1. Configure `CORSEnabled: true`, `CORSAllowedOrigins: ["*.ethereum.org"]`.
2. Send an HTTP request to the gateway with header `Origin: https://evilethereum.org`.
3. Observe `isAllowedOrigin` computing `allowedHost = "ethereum.org"` and `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluating to `true`.
4. Response includes `Access-Control-Allow-Origin: https://evilethereum.org`, confirming the bypass.
5. This can be codified as a Go unit test extending the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` pattern in `core/services/gateway/network/httpserver_test.go`, asserting that `evilethereum.org` is rejected (currently it is incorrectly accepted).

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

**File:** core/services/gateway/network/httpserver.go (L195-203)
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
