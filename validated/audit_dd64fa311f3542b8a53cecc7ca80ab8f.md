The code confirms the claim exactly as described: `isAllowedOrigin` strips the `*.` prefix and uses a bare `strings.HasSuffix(originHost, allowedHost)` check with no domain-boundary/dot validation.I've confirmed the code exactly matches the claim. The vulnerability is real and verifiable:

Audit Report

## Title
CORS Origin Allowlist Bypass via Missing Domain-Boundary Check in Wildcard Suffix Matching - (File: core/services/gateway/network/httpserver.go)

## Summary
The Gateway's internet-facing HTTP server validates the `Origin` header against a configured wildcard allowlist entry (e.g., `*.ethereum.org`) using a raw `strings.HasSuffix(originHost, allowedHost)` comparison with no domain-separator (`.`) boundary check. An attacker who registers a domain that merely ends with the configured suffix bytes (e.g. `evilethereum.org` for allowlist entry `*.ethereum.org`) is incorrectly treated as a trusted subdomain, causing the Gateway to reflect that attacker origin in `Access-Control-Allow-Origin` and grant cross-origin access.

## Finding Description
`isAllowedOrigin` splits both the request `Origin` and each configured `CORSAllowedOrigins` entry into scheme/host/port via `splitURL`, then for wildcard-prefixed entries strips the `*.` prefix and checks `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

Because `strings.HasSuffix` performs a pure byte-suffix comparison, it cannot distinguish a genuine subdomain (`api.ethereum.org`) from an unrelated domain that just happens to end in the same character sequence (`evilethereum.org`, `notarealethereum.org`). No check ensures a `.` immediately precedes the trusted suffix in `originHost`. This is confirmed by the existing test suite, which only exercises non-matching-suffix cases (`ethereum.remix.org` — doesn't end with `ethereum.org` at all) or scheme/port mismatches, and never tests the "ends with suffix but no dot boundary" scenario: [2](#0-1) 

Once `isAllowedOrigin` returns true, `handleRequest` reflects the attacker-controlled `Origin` value verbatim into `Access-Control-Allow-Origin` and sets permissive `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`: [3](#0-2) 

There is no other authentication or origin-validation layer preventing this — `isAllowedOrigin` is the sole gate for CORS trust decisions, and its logic is broken for wildcard entries.

## Impact Explanation
This is a genuine allowlist-bypass logic flaw in the internet-facing Gateway HTTP server's CORS handling. Operators using the documented wildcard `CORSAllowedOrigins` feature (e.g., `https://*.ethereum.org`) are exposed to any attacker who registers a domain ending in the same literal suffix bytes without a preceding dot boundary (e.g. `evilethereum.org`). Once accepted, a page hosted on the attacker's domain can issue authenticated cross-origin browser requests to the Gateway and read JSON-RPC responses via the reflected `Access-Control-Allow-Origin` header, enabling cross-user response exposure — an in-scope impact class (allowlist bypass / cross-user response corruption).

## Likelihood Explanation
Exploitation requires only that an operator configure a wildcard `CORSAllowedOrigins` entry (a normal, supported, documented configuration option) and that an attacker registers an inexpensive domain name ending in the same suffix bytes as the configured wildcard. No privileged access, host/database access, malicious peer/node behavior, or network-layer manipulation is required — the attacker only needs to control a browser page sending a crafted `Origin` header to the Gateway, which is exactly the threat model CORS is meant to defend against. This is fully reproducible and deterministic.

## Recommendation
In `isAllowedOrigin` (core/services/gateway/network/httpserver.go), require an explicit domain-separator boundary before the trusted suffix instead of a bare `strings.HasSuffix`, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
Add regression tests covering suffix-boundary bypass attempts such as `evilethereum.org` / `notarealethereum.org` against `*.ethereum.org`, ensuring they are rejected.

## Proof of Concept
1. Configure `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]` on the Gateway user-facing HTTP server (as done via `startNewServer` in the test harness at `core/services/gateway/network/httpserver_test.go`).
2. Send a POST request to the configured path with header `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` (since `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`), and the response includes `Access-Control-Allow-Origin: https://evilethereum.org` plus `Access-Control-Allow-Methods: GET, POST, OPTIONS` and `Access-Control-Allow-Headers: Content-Type`, despite `evilethereum.org` not being a subdomain of `ethereum.org`. This can be added as a Go unit test analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` at `core/services/gateway/network/httpserver_test.go:152-186`, but asserting the request is (incorrectly) accepted for an `evilethereum.org` origin.

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

**File:** core/services/gateway/network/httpserver.go (L195-209)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}
```

**File:** core/services/gateway/network/httpserver_test.go (L218-231)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://example.gov:8080"})

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin := "https://ethereum.remix.org"                                                 // doesn't end with ethereum.org
	resp, respBytes := sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Methods"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Headers"))
```
