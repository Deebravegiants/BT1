## Analysis

The reported bug class — overly permissive origin/allowlist matching that fails to enforce strict host-boundary checks (allowing arbitrary domains that merely share a substring/suffix with the intended one) — has a direct analog in the Chainlink Gateway's CORS origin-allowlist implementation. [1](#0-0) 

### Title
CORS Wildcard Origin Allowlist Bypass via Improper Suffix Matching - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's `isAllowedOrigin` function implements wildcard subdomain matching for `CORSAllowedOrigins` (e.g. `*.remix.com`) using `strings.HasSuffix(originHost, allowedHost)` after stripping the `*.` prefix. This check does not verify a dot (`.`) boundary between the stripped suffix and the rest of the origin host, so any domain that ends with the allowed suffix — not just true subdomains — is accepted as a valid CORS origin.

### Finding Description
In `isAllowedOrigin` [2](#0-1) , when a configured allowed origin starts with `*.` (e.g. `*.remix.com`), the code strips the `*.` prefix leaving `remix.com`, then checks `strings.HasSuffix(originHost, allowedHost)`. Because `HasSuffix` performs a raw string suffix comparison with no dot-boundary enforcement, a request `Origin` header of e.g. `https://evilremix.com` or `https://notremix.com` will satisfy `HasSuffix("evilremix.com", "remix.com") == true`, even though `evilremix.com` is an entirely unrelated, attacker-registrable domain and not a subdomain of `remix.com`.

This is called from `handleRequest` [3](#0-2) , which is the request path invoked for every unprivileged client HTTP request hitting the Gateway's user-facing endpoint (the "internet-facing gateway" handler for message envelopes described in the config: `HTTPServerConfig.CORSAllowedOrigins` / `CORSEnabled`) [4](#0-3) . When `isAllowedOrigin` returns true, the server reflects the attacker-controlled `Origin` value back in `Access-Control-Allow-Origin` and also sets `Access-Control-Allow-Headers: Content-Type`, allowing a browser running on the attacker's spoofed domain to make authenticated cross-origin requests to the Gateway and read the JSON responses directly in-browser.

This mirrors the report's root cause exactly: an allowlist regex/suffix check that is supposed to restrict access to a trusted domain and its subdomains, but instead permits any domain sharing the tail-end string, defeating the purpose of the origin allowlist (analogous to `beta.test.solflare.com` or `..solflare.com`-style bypasses in the report).

### Impact Explanation
An operator who configures a wildcard CORS allow entry (e.g. `*.mycompany.com`) to permit only their own subdomains inadvertently permits any registrable domain ending in that suffix (e.g. `evilmycompany.com`, `attacker-mycompany.com`). A malicious actor who registers such a domain and lures a victim (e.g. a Gateway operator or DON node UI user) to visit a page under their control can issue cross-origin `fetch`/`XHR` requests to the Gateway's HTTP endpoint from the victim's browser; because the malicious origin passes the allowlist check, the Gateway will reflect `Access-Control-Allow-Origin` for that origin, letting the attacker's page read Gateway responses that would otherwise be same-origin protected. Depending on what the Gateway endpoint exposes to callers (message routing/proxied node responses), this can lead to unauthorized cross-user response disclosure.

### Likelihood Explanation
Exploitability requires: (1) an operator configuring a wildcard CORS entry (a documented, supported feature — see the wildcard test cases) [5](#0-4) , and (2) an attacker registering/controlling a domain with the matching suffix and getting a victim's browser to send requests. This is a realistic and low-cost attack for any operator using wildcard-based CORS configuration, which the existing test suite indicates is an expected, supported use case.

### Recommendation
Enforce a proper subdomain boundary check instead of raw suffix matching, e.g. require that `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)` (so that `evilremix.com` does not match `remix.com`, but `foo.remix.com` does). Add negative test cases (e.g. `evilremix.com`, `notremix.com`) alongside the existing wildcard tests to prevent regression.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled=true` and `CORSAllowedOrigins=["https://*.remix.com"]`.
2. Send an HTTP request to the Gateway's configured path with header `Origin: https://evilremix.com`.
3. Observe that `isAllowedOrigin` returns `true` (since `strings.HasSuffix("evilremix.com", "remix.com")` is `true`), and the response includes `Access-Control-Allow-Origin: https://evilremix.com`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, confirming the attacker-controlled origin is treated as trusted. [6](#0-5)

### Citations

**File:** core/services/gateway/network/httpserver.go (L53-54)
```go
	CORSEnabled            bool
	CORSAllowedOrigins     []string
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
