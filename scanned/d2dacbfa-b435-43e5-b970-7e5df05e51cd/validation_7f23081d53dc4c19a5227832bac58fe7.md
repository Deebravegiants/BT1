### Title
CORS wildcard-origin allowlist bypass via missing label-boundary check enables origin spoofing - ([File: core/services/gateway/network/httpserver.go])

### Summary
The gateway's `UserServerConfig` CORS handler validates the `Origin` header against `CORSAllowedOrigins` using a suffix comparison that does not enforce a domain-label boundary (a leading `.`), allowing an attacker-controlled domain that merely ends with the same characters as an allowed suffix to be treated as an allowed subdomain, echoing `Access-Control-Allow-Origin` for that attacker origin.

### Finding Description
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` compares the incoming `Origin` header against each configured allowed origin. For entries using the `*.` wildcard prefix, it strips the `*.` and performs a bare `strings.HasSuffix(originHost, allowedHost)` check: [1](#0-0) 

Because `HasSuffix` matches on raw string suffix rather than a DNS label boundary, an origin such as `evilethereum.org` will satisfy `HasSuffix("evilethereum.org", "ethereum.org")` even though it is a completely different registrable domain than any subdomain of `ethereum.org`. The intended semantics of a wildcard entry like `https://*.ethereum.org` (allow only `*.ethereum.org` subdomains) are violated: any domain that happens to end with the literal string `ethereum.org` (e.g. `notethereum.org`, `fakeethereum.org`, `attacker-ethereum.org`) is incorrectly treated as an allowed origin.

This is called from `handleRequest`, which is the entry point for every request hitting the gateway's user-facing HTTP server: [2](#0-1) 

When `isAllowedOrigin` incorrectly returns `true`, the server sets `Access-Control-Allow-Origin` to the attacker's spoofed origin, permitting browser-based cross-origin reads of the gateway's JSON-RPC responses (message envelopes) from a domain the operator never intended to trust — this is directly analogous to the CVE's "origin spoofing" bug class (a same-origin/allowlist boundary check that fails to properly delimit the trusted origin string).

### Impact Explanation
Any unprivileged web page hosted on a domain crafted to end with the operator's configured allowed suffix (no privileged access needed — just domain registration/typosquatting) can pass the CORS allowlist check and receive cross-origin responses from the gateway's `/user` endpoint, including responses meant only for legitimate DON-integrated origins. This is a cross-user/cross-origin response confusion and allowlist-bypass issue in the internet-facing gateway component.

### Likelihood Explanation
Exploitability requires: (1) the operator enabling `CORSEnabled = true` with at least one `*.`-prefixed wildcard entry in `CORSAllowedOrigins` (a documented, supported configuration pattern, as seen in the test suite using `https://*.ethereum.org`), and (2) an attacker registering or controlling a domain whose string ends with the same substring. This is a realistic and low-cost attack (e.g., registering `evil-ethereum.org` or similar) and needs no special privileges — it is purely an unprivileged network client sending crafted `Origin` headers.

### Recommendation
Fix the wildcard suffix check to require a proper DNS label boundary, e.g. verify `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `HasSuffix`, so `evilethereum.org` cannot match `ethereum.org`.

### Proof of Concept
Given gateway config:
```
CORSEnabled = true
CORSAllowedOrigins = ["https://*.ethereum.org"]
```
An attacker serves a page from `https://evilethereum.org` and issues a cross-origin fetch to the gateway's `/user` path with header `Origin: https://evilethereum.org`. `splitURL` yields `originHost = "evilethereum.org"`; after stripping `*.` from the configured entry, `allowedHost = "ethereum.org"`; `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, so `isAllowedOrigin` returns `true` and the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker's page read the JSON-RPC response via the browser's fetch API — this is testable by extending the existing test in `core/services/gateway/network/httpserver_test.go` (`TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`) with an origin like `https://evilethereum.org` and observing the CORS header is (incorrectly) set. [3](#0-2)

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

**File:** core/services/gateway/network/httpserver_test.go (L152-165)
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
