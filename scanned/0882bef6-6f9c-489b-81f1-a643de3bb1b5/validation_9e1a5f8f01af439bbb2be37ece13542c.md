### Title
CORS wildcard-origin allowlist bypass via missing subdomain boundary check enables cross-origin request forgery against the Gateway user-facing API - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's public-facing `UserServerConfig` HTTP endpoint implements a custom CORS origin validator, `isAllowedOrigin`, that supports wildcard allowlist entries such as `*.example.com`. The wildcard match is implemented with a raw `strings.HasSuffix` check that does not require a `.` boundary before the suffix, allowing any domain that merely *ends with* the configured suffix (not just true subdomains) to be treated as an allowed origin.

### Finding Description
`isAllowedOrigin` normalizes the request's `Origin` header and each configured allowed origin via `splitURL`, then matches scheme, port, and host [1](#0-0) . For wildcard entries, it strips the `*.` prefix and does a bare suffix comparison:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

Because there is no check that the character preceding the matched suffix is a `.` (or that `originHost` boundary is a subdomain separator), an operator-configured entry like `*.ethereum.org` (intended to allow only `foo.ethereum.org`, `bar.ethereum.org`, etc.) will also match an attacker-registered domain such as `evilethereum.org`, `notethereum.org`, or `myethereum.org` — none of which are subdomains of `ethereum.org`. This is exactly the class of bug described in CVE-2024-23271: "improved checks" needed to prevent "unexpected cross-origin behavior" caused by loose origin-matching logic.

When the request's `Origin` passes `isAllowedOrigin`, the handler reflects the request's own `Origin` value back in `Access-Control-Allow-Origin` [3](#0-2) , meaning the attacker-controlled origin is granted read access to the JSON-RPC response of the gateway's `/user` endpoint from browser JavaScript.

### Impact Explanation
This endpoint is the Gateway's internet-facing user API (`UserServerConfig`), reachable by any unauthenticated web client; it is explicitly designed to be exposed to third-party frontends (e.g., `https://remix.ethereum.org` in test configs and integration tests) [4](#0-3) . An attacker who registers a domain that merely ends with the same suffix as an allowed wildcard (no subdomain relationship required) can host a malicious page that issues cross-origin, credentialed-style requests to the Gateway user API and read the JSON-RPC responses in the browser, bypassing the intended origin allowlist. Depending on what the deployed `Handlers`/DON services expose over `/user` (e.g., vault secrets metadata, workflow requests, or other gateway-routed operations), this can lead to cross-user response confusion or unauthorized use of the gateway on behalf of a victim's browser session.

### Likelihood Explanation
Exploitation requires only that: (1) the gateway operator uses a wildcard entry in `CORSAllowedOrigins` (a documented, supported pattern, as shown by the test suite covering wildcard origins [5](#0-4) ), and (2) the attacker registers or controls any domain sharing the suffix string. No authentication, node compromise, or privileged access is needed — only a victim visiting the attacker's page while the gateway is reachable. This is a plausible, low-effort attack for a public-facing DON gateway.

### Recommendation
Fix the wildcard suffix check to require a proper subdomain boundary, e.g.:
```go
if strings.HasSuffix(originHost, allowedHost) &&
   (originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)) {
    return true
}
```
or equivalently split `originHost` on `.` and compare the trailing labels exactly to `allowedHost`'s labels.

### Proof of Concept
1. Configure the gateway's `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]` (a realistic operator intent to allow only `*.ethereum.org` subdomains, mirroring the pattern shown in `core/services/gateway/integration_tests/gateway_integration_test.go`).
2. From a browser, host a page at `https://evilethereum.org` (an attacker-registered domain that is NOT a subdomain of `ethereum.org` but shares the string suffix).
3. Send a `POST` request with `fetch` (mode `cors`) to the gateway's `/user` path, with `Origin: https://evilethereum.org`.
4. Observe in `isAllowedOrigin` (`core/services/gateway/network/httpserver.go:184-190`) that `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, causing the server to respond with `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker's page read the JSON-RPC response cross-origin — violating the operator's intended allowlist.

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-179)
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
```

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

**File:** core/services/gateway/integration_tests/gateway_integration_test.go (L51-60)
```go
[UserServerConfig]
Path = "/user"
Port = 0
ContentTypeHeader = "application/jsonrpc"
MaxRequestBytes = 20_000
ReadTimeoutMillis = 1000
RequestTimeoutMillis = 1000
WriteTimeoutMillis = 1000
CORSEnabled = true
CORSAllowedOrigins = ["https://remix.ethereum.org"]
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
