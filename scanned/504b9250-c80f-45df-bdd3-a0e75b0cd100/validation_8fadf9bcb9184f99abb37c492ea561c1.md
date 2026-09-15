### Title
CORS origin allowlist tailmatch bypass via unanchored suffix comparison - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Chainlink Gateway's CORS origin-allowlist check performs a "tailmatch" (suffix) comparison to support wildcard domains (e.g. `*.ethereum.org`) but never verifies that the matched suffix is preceded by a domain-label boundary (a `.`). This is the same class of bug as CVE-2013-1944 (curl cookie domain tailmatch): a hostname like `evilethereum.org` will be treated as a subdomain of `ethereum.org` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.

### Finding Description
`httpServer.isAllowedOrigin` in [1](#0-0)  parses the request's `Origin` header and each configured `CORSAllowedOrigins` entry. For exact hosts it compares with `==`, which is safe. For wildcard entries (prefixed with `*.`), it strips the `*.` and then does:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

There is no check that `originHost` has a literal `.` immediately before the matched `allowedHost` suffix. As a result, any origin host that merely *ends with the same characters* as the allowed domain — without being an actual subdomain — is accepted. For example, if the operator configures `CORSAllowedOrigins: ["https://*.ethereum.org"]`, then `allowedHost` becomes `ethereum.org`, and an attacker-registered domain such as `https://evilethereum.org` or `https://not-ethereum.org` will incorrectly satisfy `strings.HasSuffix(originHost, "ethereum.org")` and be treated as an allowed CORS origin.

This function is invoked directly from `handleRequest`, which is the entry point for all unauthenticated/unprivileged client HTTP requests to the gateway: [3](#0-2) . When `isAllowedOrigin` returns true, the server reflects the attacker-supplied `Origin` value back in the `Access-Control-Allow-Origin` response header and enables `GET, POST, OPTIONS` / `Content-Type` cross-origin access.

### Impact Explanation
An attacker who registers a domain ending in the same label sequence as an allowed wildcard domain (trivial and cheap to do, exactly as noted in the original curl advisory) can host a malicious web page that, when visited by a victim's browser, is granted CORS access to the gateway. Since the gateway reflects the attacker's `Origin` and sets permissive CORS headers, browser-based cross-origin requests from the attacker's page can read the gateway's JSON-RPC responses (`ProcessRequest` results) that would otherwise be same-origin-restricted. This is a cross-origin response confusion / allowlist bypass reachable by any unprivileged, unauthenticated web client capable of getting a victim to load a page.

### Likelihood Explanation
High likelihood for any deployment using wildcard CORS origins (`*.domain.com`) in `CORSAllowedOrigins` — a documented, supported configuration pattern per the test suite (`TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` at [4](#0-3) ). Exploitation only requires registering a domain with the matching suffix (no dot) and getting any target to load attacker-controlled content in a browser — no privileged access or node/peer compromise needed.

### Recommendation
Anchor the suffix match to a domain-label boundary, e.g.:
```go
if strings.HasSuffix(originHost, allowedHost) &&
   (originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)) {
    return true
}
```
This mirrors the fix applied to libcurl's cookie tailmatching (requiring a `.` immediately preceding the matched suffix, or an exact match) and prevents unrelated domains sharing a substring suffix from being misclassified as subdomains.

### Proof of Concept
Given gateway config: `CORSAllowedOrigins: ["https://*.ethereum.org"]`

1. Attacker hosts a page at `https://evilethereum.org`.
2. Victim's browser (having loaded that page) sends a fetch/XHR request to the gateway's HTTP endpoint with header `Origin: https://evilethereum.org`.
3. `isAllowedOrigin` computes `allowedHost = "ethereum.org"`, `originHost = "evilethereum.org"`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates `true`.
4. The gateway responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker's page to read the JSON-RPC response cross-origin, even though `evilethereum.org` is not a subdomain of the allowed `ethereum.org` domain.

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
