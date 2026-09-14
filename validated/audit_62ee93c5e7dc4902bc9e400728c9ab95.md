### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's CORS origin validation in `isAllowedOrigin` uses `strings.HasSuffix` to match wildcard-configured allowed origins against the incoming `Origin` header, but never verifies that the suffix match is anchored on a domain-label boundary (i.e., preceded by a `.`). This is the same bug class as CVE-2022-27779: a string-suffix check intended to enforce a domain relationship (subdomain-of / TLD-of) is satisfied by an unrelated domain that merely happens to end with the same characters.

### Finding Description
`isAllowedOrigin` splits both the request's `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port, and for wildcard entries (`*.example.com`) strips the `*.` prefix and checks the origin host with a bare suffix comparison: [1](#0-0) 

Specifically:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
There is no check that `originHost` is either exactly `allowedHost` or ends with `"." + allowedHost`. As a result, an attacker-controlled domain such as `evilethereum.org` will satisfy `strings.HasSuffix("evilethereum.org", "ethereum.org")` even though it is not a subdomain of `ethereum.org`, exactly analogous to how curl's cookie domain check for `example.com.` matched an unrelated TLD due to a missing boundary check.

This function is invoked from `handleRequest`, the entry point for all requests to the internet-facing gateway HTTP server: [2](#0-1) 

If the origin passes this flawed check, the server reflects the caller-supplied `Origin` value back in `Access-Control-Allow-Origin`, along with permissive methods/headers: [3](#0-2) 

### Impact Explanation
An operator who configures a wildcard CORS allowlist entry like `https://*.ethereum.org` intends to trust only genuine subdomains of `ethereum.org`. Due to the unanchored suffix match, any attacker who registers a domain ending in the same characters (e.g., `evilethereum.org`, or more subtly a domain like `xethereum.org`) is treated as a fully trusted origin. Browsers running on the attacker's page will then have their cross-origin `fetch`/XHR requests to the gateway approved via `Access-Control-Allow-Origin`, enabling the attacker's page to read gateway JSON-RPC responses that a victim's browser is tricked into requesting (e.g. via any bearer/session material available client-side), constituting cross-user response exposure/allowlist bypass at the internet-facing gateway boundary.

### Likelihood Explanation
Exploitation requires only that an operator configure a wildcard CORS entry (a documented/supported feature, exercised in `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`) and that an attacker registers a domain string ending in the same suffix — no privileged access or network position is needed, only DNS registration of a lookalike domain, making this practically reachable from any unprivileged client/browser.

### Recommendation
Fix `isAllowedOrigin` to anchor the wildcard match on a label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".example.com"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
i.e., require the matched suffix to include the leading dot (`"."+allowedHost`) rather than the bare `allowedHost`, so `evilethereum.org` no longer matches `*.ethereum.org`.

### Proof of Concept
1. Configure the gateway with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.ethereum.org"}` (as done in `startNewServer` in the test file).
2. Send a request with header `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` (per the code path shown above) and the response contains `Access-Control-Allow-Origin: https://evilethereum.org`, even though `evilethereum.org` is unrelated to `ethereum.org`. [4](#0-3)

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
