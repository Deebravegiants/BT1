Audit Report

## Title
CORS allowlist bypass via improper wildcard-suffix domain matching in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

## Summary
`httpServer.isAllowedOrigin` implements wildcard CORS entries (e.g. `*.ethereum.org`) by stripping the `*.` prefix and checking `strings.HasSuffix(originHost, allowedHost)` with no domain-boundary (dot) enforcement before the suffix. This lets an attacker-registered domain that merely ends with the allowed suffix (e.g. `evilethereum.org`) be treated as a trusted subdomain, causing the Gateway to reflect the attacker's `Origin` in `Access-Control-Allow-Origin` and permit cross-origin reads of JSON-RPC responses.

## Finding Description
`isAllowedOrigin` parses the incoming `Origin` and each configured allowlist entry via `splitURL`, matches scheme and port, and for entries prefixed with `*.` performs: [1](#0-0) 
Because `strings.HasSuffix` only checks that `originHost` ends with `allowedHost`, and no check enforces that the preceding character is a `.` (or that the match is the entire host), a domain such as `evilethereum.org` satisfies `HasSuffix("evilethereum.org", "ethereum.org")` even though it is not a subdomain of `ethereum.org`. This function is invoked directly from the unauthenticated request path: [2](#0-1) 
There is no other validation layer (auth middleware, signature check, or additional origin normalization) between the client-supplied `Origin` header and this comparison, so the flawed suffix check is the sole gate for the wildcard-CORS allowlist. The existing test suite exercises only the legitimate case (`https://remix.ethereum.org` against `https://*.ethereum.org`), which does not catch the boundary-less suffix match: [3](#0-2) 

## Impact Explanation
When an operator enables `CORSEnabled` with a wildcard entry in `CORSAllowedOrigins` (a supported, documented configuration used in the codebase's own tests), an attacker who registers a domain that ends with the same suffix without a dot boundary (e.g. `evilethereum.org`) gets `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers` set for their look-alike origin. This is a genuine allowlist-bypass in the CORS domain-matching logic itself (not an operator misconfiguration of an otherwise-secure default), matching the in-scope "allowlist bypass" impact class, and lets a page on the attacker's confusable domain read cross-origin responses from the Gateway's JSON-RPC endpoint that a browser would otherwise block under Same-Origin Policy.

## Likelihood Explanation
Exploitation requires only (1) the operator to use the wildcard CORS feature as designed — not a misuse of the feature — and (2) the attacker registering a cheap look-alike domain with no dot boundary before the allowed suffix. No node compromise, credential leakage, or privileged access is needed; a normal browser or HTTP client automatically sets the `Origin` header on cross-origin requests, making this trivially and repeatably triggerable by an unprivileged remote actor.

## Recommendation
Enforce a domain boundary in the wildcard match, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This rejects `evilethereum.org` while still correctly matching `remix.ethereum.org` and `ethereum.org`.

## Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send an HTTP request to the Gateway endpoint with header `Origin: https://evilethereum.org`.
3. Observe the response contains `Access-Control-Allow-Origin: https://evilethereum.org` (via `strings.HasSuffix("evilethereum.org", "ethereum.org")` returning `true` at core/services/gateway/network/httpserver.go:187), confirming the attacker's non-subdomain origin is incorrectly allowlisted. A Go unit test mirroring `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` but asserting `evilethereum.org` is rejected would fail against current code, proving the bug.

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

**File:** core/services/gateway/network/httpserver_test.go (L152-166)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://*.gov"})

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin := "https://remix.ethereum.org"
	resp, respBytes := sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))

```
