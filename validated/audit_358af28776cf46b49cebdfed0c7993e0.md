Audit Report

## Title
CORS Wildcard-Origin Allowlist Bypass via Missing Dot-Boundary Check - (File: core/services/gateway/network/httpserver.go)

## Summary
`httpServer.isAllowedOrigin` implements wildcard origin matching (`*.example.com`) using a raw `strings.HasSuffix` comparison on the origin host against the wildcard's suffix, with no requirement that a `.` label boundary precede the matched suffix. This lets an attacker whose domain merely ends with the same characters as an allowed suffix (e.g. `evilethereum.org` matching allowlist entry `*.ethereum.org`) pass origin validation and receive a reflected `Access-Control-Allow-Origin` header for their own, unrelated domain.

## Finding Description
In `isAllowedOrigin`, for a wildcard-configured allowed origin, the code strips the `"*."` prefix and then does `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 
Because this is a pure string-suffix check rather than a label-aware subdomain check, `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates to `true` even though `evilethereum.org` is a completely separate, attacker-registrable domain and not a subdomain of `ethereum.org`. This result is then used directly in `handleRequest` to reflect the attacker's `Origin` header value into `Access-Control-Allow-Origin`: [2](#0-1) 
The existing test suite exercises only non-matching cases such as `ethereum.remix.org` (correctly rejected because the suffix characters don't even line up) and never tests the sibling-domain bypass case (e.g. `evilethereum.org` vs `*.ethereum.org`), so this exact bug is untested and unguarded: [3](#0-2) 
This is the CWE-346 (Origin Validation Error) bug class: an untrusted origin is incorrectly treated as trusted due to insufficiently strict validation logic.

## Impact Explanation
When an operator enables CORS (`CORSEnabled = true`) with a wildcard entry in `CORSAllowedOrigins` — a supported, documented configuration pattern per the sample config files and covered by dedicated wildcard tests in the codebase — an attacker who registers a low-cost sibling domain (e.g. `evilethereum.org`) can have a page on that domain make cross-origin requests to the Gateway's HTTP server (e.g. `UserServerConfig`). The server will reflect the attacker's `Origin` into `Access-Control-Allow-Origin`, letting attacker-controlled JavaScript read cross-origin JSON-RPC responses that a victim's browser would otherwise not be permitted to access. This maps to the in-scope "allowlist bypass" / "cross-user response corruption" impact category for the Gateway component.

## Likelihood Explanation
Exploitation requires no privileged access, credentials, or victim social engineering beyond normal browser use of a page hosted on the attacker's domain. It only requires (1) the operator to use a wildcard `CORSAllowedOrigins` entry — an intended, supported configuration feature rather than a misconfiguration — and (2) the attacker to register any domain sharing the same trailing characters as the configured wildcard suffix. This is directly reachable over the internet-facing Gateway HTTP server and is fully reproducible/deterministic.

## Recommendation
Fix the wildcard suffix check to require a proper label boundary before the matched suffix, e.g. compare against `"."+suffix` (or verify `originHost == suffix || strings.HasSuffix(originHost, "."+suffix)`) instead of a bare `strings.HasSuffix` call. Add regression tests for sibling-domain bypass attempts (e.g. `evilethereum.org` against `*.ethereum.org`) to `httpserver_test.go`.

## Proof of Concept
1. Configure the Gateway's `HTTPServerConfig` (e.g. `UserServerConfig`) with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send an HTTP request to the Gateway endpoint with header `Origin: https://evilethereum.org`.
3. `isAllowedOrigin` strips `"*."` to get `allowedHost = "ethereum.org"` and evaluates `strings.HasSuffix("evilethereum.org", "ethereum.org")`, which returns `true`.
4. The response includes `Access-Control-Allow-Origin: https://evilethereum.org`, confirming a page on the attacker-registered `evilethereum.org` domain is granted CORS access despite not being a subdomain of `ethereum.org`. This can be verified as a new unit test in `core/services/gateway/network/httpserver_test.go` analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` but asserting the header IS set (demonstrating the bypass) for the `evilethereum.org` origin.

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

**File:** core/services/gateway/network/httpserver_test.go (L218-232)
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
