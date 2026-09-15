Audit Report

## Title
CORS wildcard-origin allowlist bypass via missing domain-boundary check in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

## Summary
The Gateway HTTP server's `isAllowedOrigin` function implements wildcard CORS origin matching using a raw `strings.HasSuffix` comparison without enforcing a domain boundary (a preceding `.` or exact match). This allows any attacker-registered domain that merely ends with the same character sequence as a configured wildcard suffix (e.g. `chain.link`) to be treated as an allowed CORS origin, even though it is not an actual subdomain.

## Finding Description
`isAllowedOrigin` parses the `Origin` header and each configured allowed origin via `splitURL`, then for entries prefixed with `*.` strips the prefix and checks `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

This is a pure string-suffix comparison with no boundary check, so `strings.HasSuffix("evilchain.link", "chain.link")` evaluates to `true` for a wildcard config of `*.chain.link`, even though `evilchain.link` is an unrelated domain, not a subdomain. This function is invoked from `handleRequest`, the entry point for every unprivileged HTTP request to the Gateway, using the attacker-controlled `Origin` header, and reflects that origin into `Access-Control-Allow-Origin` when the check passes: [2](#0-1) 

No other validation exists in this path — scheme and port are checked for equality, and host is checked for exact match before falling through to the flawed suffix check, so there is no mitigating boundary logic elsewhere in the function: [3](#0-2) 

The existing test suite only exercises legitimate subdomains (`remix.ethereum.org`, `another.valid.domain.com`, `example.gov`) and does not test the boundary-bypass case (e.g. `evilethereum.org` against `*.ethereum.org`), confirming this bug is neither caught nor fixed by current tests: [4](#0-3) 

## Impact Explanation
This is a genuine allowlist bypass bug in the Gateway's CORS implementation, matching the in-scope "allowlist bypass" impact category. When an operator configures a wildcard `CORSAllowedOrigins` entry (a normal, supported, documented configuration feature — not a misconfiguration), any attacker able to register a domain ending in the same string as the configured suffix can have their origin falsely treated as trusted, receiving `Access-Control-Allow-Origin` reflecting their domain and enabling unauthorized cross-origin requests against the Gateway API from that domain.

## Likelihood Explanation
No special privilege or network position is needed — the wildcard matching path is a standard, documented configuration option, and exploitation requires only crafting an HTTP `Origin` header, or registering a domain ending with the target suffix. This is triggerable purely via a normal, unprivileged HTTP request to the Gateway's public endpoint.

## Recommendation
Fix `isAllowedOrigin` to enforce a proper domain boundary in the wildcard branch, e.g., require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix` check, so that only true subdomains of the configured domain match.

## Proof of Concept
1. Start the Gateway HTTP server with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.ethereum.org"}` (as in `startNewServer` in `httpserver_test.go`).
2. Send a POST request to the server with header `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, confirming the unrelated domain `evilethereum.org` is incorrectly treated as a trusted subdomain of `ethereum.org`.
4. This can be added as a unit test extending `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` asserting that such an origin is rejected (currently it is incorrectly accepted).

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

**File:** core/services/gateway/network/httpserver_test.go (L152-186)
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

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "https://another.valid.domain.com"
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "http://example.gov"
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))
}
```
