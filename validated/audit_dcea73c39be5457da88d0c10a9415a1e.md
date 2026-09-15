### Title
CORS wildcard-origin allowlist bypass via suffix matching without domain-boundary check - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's internet-facing JSON-RPC user server (`UserServerConfig`, `ContentTypeHeader = "application/jsonrpc"`) implements a custom CORS allowlist check in `isAllowedOrigin` that matches wildcard entries (e.g. `*.ethereum.org`) using plain string-suffix comparison instead of a proper subdomain-boundary check. This allows an attacker who registers an unrelated sibling domain to be treated as an allowed origin, directly analogous to the overly permissive CORS whitelist described in CVE-2017-14460 for Parity's JSON-RPC endpoint.

### Finding Description
The gateway's `isAllowedOrigin` function is used to decide whether to reflect `Access-Control-Allow-Origin` for incoming requests to the gateway's JSON-RPC endpoint: [1](#0-0) 

For wildcard entries, the code strips the `*.` prefix and then only checks that the origin host **ends with** the remaining string:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

There is no check that the character immediately preceding the matched suffix is a `.` (i.e., a true subdomain boundary). As a result, for an allowlist entry `*.ethereum.org` (stripped to `ethereum.org`), any origin host that simply ends with the literal characters `ethereum.org` will pass — including a completely unrelated, attacker-registered domain such as `evilethereum.org` or `myethereum.org`, which is not a subdomain of `ethereum.org` at all but a sibling second-level domain the attacker can freely register.

This is used on the gateway's public-facing JSON-RPC user server, whose CORS configuration is exercised by config such as: [2](#0-1) 

and tested only for legitimate subdomain cases, never for the sibling-domain bypass: [3](#0-2) 

When a request from the attacker's origin is allowed, the handler reflects the origin in the CORS headers and processes the JSON-RPC request: [4](#0-3) 

### Impact Explanation
An unprivileged remote attacker who lures a victim to a malicious website hosted on a domain crafted to end with an allowed wildcard suffix (e.g., registering `xethereum.org` when the node operator intended to allow only `*.ethereum.org` subdomains) can have their page's cross-origin JavaScript read responses from the gateway's JSON-RPC endpoint that the operator did not intend to expose to that origin. This effectively bypasses the CORS allowlist/quota control that operators configure to restrict which web origins may interact with the gateway, matching the "allowlist bypass" and "cross-user response confusion" impact classes for an internet-facing JSON-RPC gateway.

### Likelihood Explanation
Exploitation requires only that the victim visit an attacker-controlled webpage while a browser session can reach the gateway's user-facing port — no privileged access is needed, mirroring the CVE-2017-14460 attack vector (victim visits malicious site; auto-sent request triggers cross-origin access). The prerequisite is that the node operator configured a wildcard subdomain entry in `CORSAllowedOrigins` (a documented, supported configuration pattern, as shown in the test suite), making this reachable whenever wildcard CORS entries are used.

### Recommendation
Fix `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` to enforce a proper subdomain boundary when matching wildcard entries — e.g., require that `originHost == allowedHost` or `originHost` ends with `"."+allowedHost`, rather than a bare `strings.HasSuffix` check. Add regression tests covering sibling-domain bypass attempts (e.g., `xethereum.org` against allowlist entry `*.ethereum.org`).

### Proof of Concept
1. Configure the gateway's `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser, load a malicious page hosted at `https://xethereum.org` (a domain the attacker legitimately registers, unrelated to `ethereum.org`).
3. Have the page issue a `fetch`/XHR request to the gateway's JSON-RPC endpoint with `Origin: https://xethereum.org`.
4. Observe that `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and `strings.HasSuffix("xethereum.org", "ethereum.org")` returns `true`, causing the server to respond with `Access-Control-Allow-Origin: https://xethereum.org`, letting the malicious page's script read the JSON-RPC response cross-origin despite not being an authorized subdomain of `ethereum.org`.

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
