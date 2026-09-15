## Finding

A genuine analog exists in the gateway's CORS allowlist wildcard matching logic, which mirrors the Envoy bug class ("wildcards/prefix domain wildcards ... causing improper validation").

### Title
CORS wildcard allowlist bypass via unanchored suffix match in Gateway HTTP server - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The Chainlink Gateway's `httpServer.isAllowedOrigin` implements wildcard-domain matching for the `CORSAllowedOrigins` allowlist by stripping the `*.` prefix and then checking `strings.HasSuffix(originHost, allowedHost)`, with no check that the match is anchored at a label (`.`) boundary. [1](#0-0) 

### Finding Description
`isAllowedOrigin` parses the scheme/host/port of the request's `Origin` header and compares it against each configured allowed origin. [2](#0-1) 

For wildcard entries like `*.ethereum.org`, the code strips the `*.` and only checks `strings.HasSuffix(originHost, "ethereum.org")`. Because this is a raw string suffix check rather than a domain-label-boundary check, any attacker-registered domain whose name simply ends with the same characters — e.g. `evil-ethereum.org` or `notethereum.org` — will also satisfy `HasSuffix`, even though it is not a subdomain of `ethereum.org`. This is functionally the same bug class as the Envoy CVE-2023-35941 root cause: a prefix/suffix wildcard domain check that is "always valid" for attacker-chosen values outside the intended domain, because the boundary between the wildcard label and the fixed suffix is not enforced.

This function directly gates `handleRequest`, the entry point for all Gateway HTTP traffic (an unauthenticated, internet-facing endpoint): [3](#0-2) 

When `isAllowedOrigin` returns true, the server sets `Access-Control-Allow-Origin` to the attacker's own (spoofed-look-alike) origin, permitting a page hosted on the attacker's domain to make cross-origin fetch/XHR requests to the Gateway and read the JSON-RPC responses in the browser, defeating the intended CORS allowlist restriction. The existing test suite only tests correctly-anchored wildcard subdomains (e.g. `remix.ethereum.org` against `*.ethereum.org`) and does not cover this boundary-bypass case. [4](#0-3) 

### Impact Explanation
This is a concrete allowlist bypass reachable by any unprivileged client capable of hosting a webpage on a domain string that shares the wildcard's suffix (no privileged access needed — domain registration is the only requirement, and doesn't even need to be a subdomain of the intended trusted domain). It undermines the operator's origin-restriction intent for the Gateway's public-facing API, allowing cross-origin browser-based reads of Gateway JSON-RPC responses that were meant to be limited to `*.ethereum.org`-style trusted front ends. This is an "allowlist bypass" per the accepted impact categories.

### Likelihood Explanation
Likelihood is moderate-to-high wherever operators configure wildcard entries in `CORSAllowedOrigins` (a documented, supported configuration pattern demonstrated in the test suite itself). Exploitation requires no credentials, no cooperation from a legitimate user beyond visiting the attacker's page, and no race conditions — only registering a domain name that happens to share the suffix.

### Recommendation
Anchor the suffix match to a domain-label boundary, e.g. require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` after stripping the `*.` prefix, so `evil-ethereum.org` no longer matches an allowlist entry of `*.ethereum.org`.

### Proof of Concept
1. Configure the Gateway with `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers/hosts a page at `https://evil-ethereum.org` (no dot separator before `ethereum.org`).
3. Attacker's page issues a `fetch()` to the Gateway's HTTP endpoint; the browser sends `Origin: https://evil-ethereum.org`.
4. `isAllowedOrigin` strips the wildcard to `ethereum.org` and calls `strings.HasSuffix("evil-ethereum.org", "ethereum.org")`, which returns `true`. [1](#0-0) 
5. The server responds with `Access-Control-Allow-Origin: https://evil-ethereum.org`, and the browser permits the attacker's script to read the Gateway's response, bypassing the intended origin restriction.

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
