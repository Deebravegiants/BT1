This confirms the bug. The gateway's `UserServerConfig` (Chainlink Functions/Gateway internet-facing endpoint, e.g. `/user` path on port 8080) is configurable with `CORSEnabled = true` and wildcard `CORSAllowedOrigins` (e.g. `["https://*.ethereum.org"]`), and the actual matching logic in `isAllowedOrigin` is vulnerable to a domain-suffix bypass analogous to the Claude Code `startsWith()` bug.

### Title
CORS Wildcard-Origin Suffix Validation Bypass Allows Any Attacker Domain Ending in the Allowed Suffix to Read Gateway Responses - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's user-facing HTTP server validates CORS `Origin` headers against a configured allowlist that supports wildcard entries like `*.remix.com`. The wildcard-matching branch strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` without requiring a `.` boundary before the suffix, so any origin host that merely ends with the allowed string (e.g., `evilremix.com`) is treated as trusted, mirroring the reported `startsWith()`-based domain bypass but on the suffix side.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  compares the request's `Origin` header host against configured `CORSAllowedOrigins`. For wildcard entries it does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
This strips `*.` and performs a raw suffix check with no separator/boundary requirement. If an operator configures `CORSAllowedOrigins = ["https://*.ethereum.org"]` (a documented, supported pattern — see the test cases at [2](#0-1) ), then `allowedHost` becomes `ethereum.org`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates to `true`, incorrectly granting `evilethereum.org` (or `attacker-owned-ethereum.org`, `notethereum.org`, etc.) status as a trusted origin — the same class of bug as `modelcontextprotocol.io.example.com` bypassing a `startsWith()` check, just anchored at the opposite string boundary.

The result of a successful bypass is set directly in `handleRequest`: [3](#0-2)  reflects the attacker's `Origin` back in `Access-Control-Allow-Origin`, permitting a browser on the attacker's domain to read the gateway's JSON-RPC response body via `fetch`/`XHR` for any unprivileged, cross-origin request to this internet-facing endpoint.

### Impact Explanation
This is a concrete allowlist bypass (CWE-601-class) reachable by any unprivileged web client that can lure a victim's browser (or make a direct cross-origin request) to hit the Gateway's `UserServerConfig` HTTP endpoint. Once the forged `Origin` passes validation, the attacker's page gains read access to responses from `ProcessRequest` [4](#0-3)  that would otherwise be restricted to legitimate allowed origins — this is the Chainlink Functions/Capabilities Gateway component that brokers requests between users and DON nodes, so leaked responses could include workflow/job results tied to other users' requests (cross-user response confusion / potential data exfiltration), which matches the "internet-facing gateway" and "allowlist bypass" impact categories in scope.

### Likelihood Explanation
Exploitability depends entirely on the deployed configuration using a wildcard entry in `CORSAllowedOrigins` with `CORSEnabled = true`. This is a documented, tested, and presumably real-world usage pattern (wildcard subdomain allowlisting is explicitly tested in [5](#0-4) ), so any operator relying on wildcard CORS origins for their Gateway deployment is exposed. No authentication or special privilege is required by the attacker — only the ability to register/control a domain that shares the allowed suffix and get a victim's browser to make a cross-origin request (or make the request via a controlled site directly).

### Recommendation
Fix `isAllowedOrigin` to require a proper subdomain boundary before applying the suffix check, e.g.:
```go
if strings.HasSuffix(originHost, allowedHost) &&
   (originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)) {
    return true
}
```
or parse and compare the label sequence rather than doing raw substring/suffix comparisons.

### Proof of Concept
1. Configure the Gateway with:
```toml
[UserServerConfig]
CORSEnabled = true
CORSAllowedOrigins = ["https://*.ethereum.org"]
```
2. From a browser page hosted at `https://evilethereum.org` (or any domain the attacker registers ending in `ethereum.org`), send a cross-origin `fetch` request to the Gateway's `/user` endpoint with `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` via the `strings.HasSuffix` check [6](#0-5) , causing the server to respond with `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker's page read the JSON-RPC response body cross-origin.

### Citations

**File:** core/services/gateway/network/httpserver.go (L33-35)
```go
type HTTPRequestHandler interface {
	ProcessRequest(ctx context.Context, rawMessage []byte, auth string) (rawResponse []byte, httpStatusCode int)
}
```

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
