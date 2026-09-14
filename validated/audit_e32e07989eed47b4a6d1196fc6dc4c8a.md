This confirms the vulnerability. The wildcard CORS origin matching in `isAllowedOrigin` uses a naive `strings.HasSuffix` check without verifying that a `.` boundary precedes the matched suffix, so a domain like `https://evilethereum.org` would incorrectly match an allowlist entry of `https://*.ethereum.org`, since `evilethereum.org` ends with `ethereum.org` as a raw string suffix, not requiring the subdomain dot separator. [1](#0-0) 

The existing tests only exercise the true-positive wildcard cases (e.g., `remix.ethereum.org` matching `*.ethereum.org`) and negative cases with unrelated domains, but never test the domain-suffix-without-dot collision case. [2](#0-1) 

This `isAllowedOrigin` result directly gates whether `Access-Control-Allow-Origin` is echoed back for the request's `Origin` header in the internet-facing gateway HTTP server, allowing cross-user response confusion/credentialed CORS reads by any unprivileged network client that can register a domain with the right suffix. [3](#0-2) 

### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
`httpServer.isAllowedOrigin` implements wildcard CORS origin matching (`*.domain.com`) by stripping the `*.` prefix and then checking `strings.HasSuffix(originHost, allowedHost)`. This is not anchored to a subdomain boundary (no check that the character immediately preceding the matched suffix is a `.`), so any origin host that merely ends with the same characters as the allowed domain — without actually being a subdomain of it — is treated as allowed.

### Finding Description
In `isAllowedOrigin`, the wildcard branch is:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [1](#0-0) 

If an operator configures `CORSAllowedOrigins = ["https://*.ethereum.org"]` intending to allow only subdomains of `ethereum.org`, the code strips the wildcard to get `allowedHost = "ethereum.org"`. It then only checks that `originHost` ends with that literal string. Any registrable domain that happens to end with those characters — e.g. `evilethereum.org`, `notethereum.org`, or `attacker-ethereum.org` — satisfies `strings.HasSuffix` and is incorrectly treated as an allowed subdomain, even though it shares no actual domain relationship with `ethereum.org`. A correct implementation would require the character preceding the matched suffix to be `.` (i.e., check `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)`).

This function directly controls whether the gateway's HTTP server reflects the `Origin` header back in `Access-Control-Allow-Origin` for the internet-facing JSON-RPC HTTP endpoint. [3](#0-2) 

### Impact Explanation
An unprivileged, remote attacker who registers a domain with the right suffix (e.g., `evilethereum.org` for an allowlist of `*.ethereum.org`) can serve a page from that domain and have browsers granted CORS access to the gateway's HTTP endpoint, including credentialed responses if any browser-stored credentials/cookies are sent with the request. This is a cross-origin allowlist bypass leading to cross-user response confusion / unauthorized data exposure via CORS, matching the "allowlist or quota bypass" and "cross-user response confusion" impact classes.

### Likelihood Explanation
Exploitation requires:
1. The gateway operator to have configured a wildcard `CORSAllowedOrigins` entry (a supported, documented feature, not experimental).
2. The attacker to control/register a domain ending in the same literal suffix as the allowed domain and lure a victim's browser to it.

Domain registration abuse of this kind (registering `evil<allowed-domain>` style names) is a well-known and low-cost attack technique, making this moderately likely wherever wildcard CORS origins are configured.

### Recommendation
Anchor the wildcard suffix match to a subdomain boundary in `isAllowedOrigin`, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
Add regression tests covering suffix-collision domains (e.g., `evilethereum.org` against `*.ethereum.org`) to prevent regressions.

### Proof of Concept
1. Configure the gateway with `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request to the gateway HTTP endpoint with header `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` (via the unanchored `strings.HasSuffix` check) and the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type` — exactly as it does for a legitimate `remix.ethereum.org` origin in the existing test `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`. [4](#0-3)

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
