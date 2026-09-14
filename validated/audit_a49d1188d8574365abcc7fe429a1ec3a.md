## Finding

The Connext/Nomad report's core theme — that allowlist-style configuration values must be validated with rigorous, precise matching logic or their protections are silently bypassed — has a concrete analog in the Chainlink Gateway's CORS origin allowlist implementation.

### Title
CORS Origin Allowlist Bypass via Improper Suffix Matching in Gateway User Server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's user-facing HTTP server enforces `CORSAllowedOrigins` using a naive `strings.HasSuffix` comparison for wildcard entries (e.g. `*.example.com`), without requiring a dot boundary before the suffix. This allows any origin whose hostname merely ends with the configured suffix — not just true subdomains — to be treated as allowed.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard origin and then checks `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

Because there is no check that the character preceding the suffix is a `.` (or that `originHost` is properly `allowedHost` or `<label>.` + `allowedHost`), a request from a host like `evil-ethereum.org` or `attackerethereum.org` will satisfy `HasSuffix("attackerethereum.org", "ethereum.org")` even though it is not a subdomain of `ethereum.org`. The intended allowlist `*.ethereum.org` is effectively `*ethereum.org`.

This logic is invoked from `handleRequest`, which sets `Access-Control-Allow-Origin` to the raw attacker-supplied `Origin` header value whenever `isAllowedOrigin` returns true: [2](#0-1) 

The existing test suite documents and exercises the wildcard matching behavior but does not test (or guard against) the boundary-less suffix bypass case: [3](#0-2) 

This is the Gateway-specific analog of `core/web/router.go`'s `uiCorsHandler`, which by contrast relies on the `gin-contrib/cors` library for exact-origin matching and does not implement custom wildcard suffix logic: [4](#0-3) 

### Impact Explanation
An operator who configures `CORSAllowedOrigins` with a wildcard entry (e.g., `https://*.mydomain.com`) — a supported and documented pattern per the Gateway config/tests — unintentionally allows any attacker-registered domain that happens to end with `mydomain.com` (e.g., `evilmydomain.com`) to receive `Access-Control-Allow-Origin` echoing their origin. A malicious web page hosted on such a domain can then issue cross-origin browser requests to the Gateway's user-facing JSON-RPC endpoint and read the response, defeating the operator's intended origin restriction. Given the Gateway brokers requests into DON/handler services (workflows, vault, confidential relay, etc.), this can lead to unauthorized cross-origin reads of responses intended to be restricted to the operator's own front-end origins.

### Likelihood Explanation
Exploitation only requires: (1) the Gateway operator to configure a wildcard CORS origin (a supported, documented configuration pattern), and (2) an attacker to register/host content on a domain sharing the suffix without a proper subdomain relationship. No privileged access or node compromise is needed — this is reachable directly from an unprivileged browser-based client making a cross-origin request with a crafted `Origin` header.

### Recommendation
Fix `isAllowedOrigin` to require a proper subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // keep leading dot, e.g. ".remix.com"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` either exactly equals the base domain or ends with `.`+baseDomain, closing the boundary-less suffix bypass. Add regression tests for hostile suffix-collision hostnames (e.g., `evil-remix.org`, `notremix.org`) to prevent regressions.

### Proof of Concept
1. Configure Gateway `UserServerConfig.CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.org"]`.
2. From a browser hosted at `https://evil-remix.org` (attacker-controlled, no relation to `remix.org`), send a cross-origin `fetch` request to the Gateway's JSON-RPC endpoint with `Origin: https://evil-remix.org`.
3. Server's `isAllowedOrigin` computes `allowedHost = "remix.org"` after stripping `*.`, then `strings.HasSuffix("evil-remix.org", "remix.org")` returns `true`.
4. Server responds with `Access-Control-Allow-Origin: https://evil-remix.org`, allowing the browser to read the response cross-origin, despite `evil-remix.org` never being an intended allowed subdomain.

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

**File:** core/web/router.go (L571-586)
```go
// Add CORS headers so UI can make api requests
func uiCorsHandler(ao string) gin.HandlerFunc {
	c := cors.Config{
		AllowMethods:     []string{"GET", "POST", "PATCH", "DELETE"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           math.MaxInt32,
	}
	if ao == "*" {
		c.AllowAllOrigins = true
	} else if allowOrigins := strings.Split(ao, ","); len(allowOrigins) > 0 {
		c.AllowOrigins = allowOrigins
	}
	return cors.New(c)
}
```
