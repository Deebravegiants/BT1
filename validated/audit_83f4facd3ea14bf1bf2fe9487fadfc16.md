### Title
CORS wildcard-subdomain suffix check in Gateway `UserServerConfig` HTTP server allows origin allowlist bypass - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Gateway's user-facing HTTP server (`UserServerConfig`) validates CORS `Origin` headers against `CORSAllowedOrigins` using `isAllowedOrigin`, which supports wildcard entries such as `*.ethereum.org`. The wildcard match is implemented with a bare `strings.HasSuffix` check that does not enforce a domain-label boundary (a leading `.`), allowing any attacker-registered domain whose name simply ends with the configured suffix — not just a genuine subdomain — to be treated as an allowed origin.

### Finding Description
In `core/services/gateway/network/httpserver.go`, `isAllowedOrigin` performs the wildcard comparison as: [1](#0-0) 
```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
After stripping `*.`, `allowedHost` becomes e.g. `ethereum.org`. The check `strings.HasSuffix(originHost, "ethereum.org")` matches any hostname ending in that literal string, including non-subdomains like `fakeethereum.org` or `notethereum.org`, which do not belong to the intended domain owner at all. A correct wildcard-subdomain check must require the character preceding the suffix to be a dot (i.e., `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)`).

This function gates the CORS response in `handleRequest`: [2](#0-1) 
When `isAllowedOrigin` returns true, the server echoes back the caller-controlled `Origin` value in `Access-Control-Allow-Origin`, and this server path also forwards any `Authorization: Bearer` token straight to the handler as `auth` for `ProcessRequest`: [3](#0-2) 

The `UserServerConfig` (of type `HTTPServerConfig` with `CORSEnabled`/`CORSAllowedOrigins`) is the internet-facing gateway HTTP endpoint that browsers/UIs use to submit JSON-RPC requests to DON handlers, as configured in `core/services/gateway/config/config.go`: [4](#0-3) 
and exercised in tests confirming the exact bypass semantics of the wildcard matcher: [5](#0-4) [6](#0-5) 

### Impact Explanation
If a node operator configures a wildcard allowed origin (e.g., `*.chainlink-ui.com`), an unrelated attacker who registers a look-alike domain that merely ends with the same string (e.g., `evilchainlink-ui.com`) can have their site's cross-origin browser requests granted `Access-Control-Allow-Origin` for that exact origin plus `Access-Control-Allow-Credentials`-style behavior for JSON-RPC responses. This lets a malicious, unprivileged web page read gateway JSON-RPC responses (including data returned by DON handlers) that a victim's browser would send with cookies/tokens, achieving cross-user/cross-origin response confusion and information disclosure comparable to the analog Nx `nx graph` CORS bug (permissive CORS letting any visited site read local server responses).

### Likelihood Explanation
Exploitability requires: (1) the gateway operator to configure a wildcard `CORSAllowedOrigins` entry (a supported, documented feature), and (2) the attacker to register or control a domain string ending in the configured suffix — which is easy and cheap to achieve (domain squatting on a suffix string, not a real subdomain). No privileged access to the gateway or DON is needed; the request originates from an ordinary browser tab, matching the "unprivileged actor" analog criteria.

### Recommendation
Fix the wildcard matching logic in `isAllowedOrigin` to enforce a label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
Add regression tests asserting that `fakeethereum.org` (and similar non-dot-boundary matches) are rejected when `*.ethereum.org` is configured.

### Proof of Concept
1. Configure Gateway `UserServerConfig.CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser page hosted at `https://fakeethereum.org` (attacker-controlled, not a subdomain of `ethereum.org`), send a fetch/XHR request to the gateway's user endpoint with `Origin: https://fakeethereum.org`.
3. Observe the server's `isAllowedOrigin` strips `*.` to `ethereum.org` and calls `strings.HasSuffix("fakeethereum.org", "ethereum.org")`, which returns `true`, causing the server to respond with `Access-Control-Allow-Origin: https://fakeethereum.org`, allowing the attacker page's script to read the JSON-RPC response cross-origin.

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

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```

**File:** core/services/gateway/config/config.go (L11-16)
```go
type GatewayConfig struct {
	UserServerConfig        gw_net.HTTPServerConfig
	NodeServerConfig        gw_net.WebSocketServerConfig
	ConnectionManagerConfig ConnectionManagerConfig
	HTTPClientConfig        gw_net.HTTPClientConfig

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

**File:** core/services/gateway/network/httpserver_test.go (L218-252)
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

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "http://another.valid.domain.org"                                            // http instead of https
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Methods"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Headers"))

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "http://example.gov"                                                         // port missing
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Methods"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Headers"))
}
```
