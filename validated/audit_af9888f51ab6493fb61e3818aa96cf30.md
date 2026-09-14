### Title
CORS Wildcard Origin Bypass via Missing Dot-Boundary Check in `isAllowedOrigin` - ([File: core/services/gateway/network/httpserver.go])

### Summary
The gateway's internet-facing HTTP server validates CORS origins with a wildcard-matching routine that checks only a raw string suffix, without requiring a subdomain-delimiting dot. An attacker-registrable domain that merely *ends with* the same characters as an allowed wildcard suffix (e.g. `evilethereum.org` vs. allowed `*.ethereum.org`) is incorrectly treated as a trusted subdomain, letting the attacker's site receive `Access-Control-Allow-Origin` clearance it should never get.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  strips the `*.` prefix from a configured wildcard origin and then does a plain `strings.HasSuffix` comparison against the incoming request's `Origin` host:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

`strings.HasSuffix` performs a pure character-suffix match, not a domain-label match. For an operator-configured wildcard such as `https://*.ethereum.org`, `allowedHost` becomes `ethereum.org`. Any origin host that ends in the literal substring `ethereum.org` — including `evilethereum.org`, `notarealethereum.org`, or `xethereum.org` — will satisfy `HasSuffix` even though none of these are subdomains of `ethereum.org` and can be freely registered by any attacker. There is no check for a preceding `.` boundary (i.e., no verification that `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`).

This function is invoked directly from the request path in `handleRequest` at [2](#0-1) , which sets `Access-Control-Allow-Origin` to the raw, attacker-supplied `Origin` header value whenever `isAllowedOrigin` returns true. This is the same bug class as CVE-2023-20873 (wildcard pattern matching allowing a security check to be bypassed by a value that superficially "matches" the allowed pattern) applied to the gateway's own CORS allowlist rather than Spring's actuator path matcher.

The existing test suite only exercises the negative case where the origin genuinely does not end with the allowed suffix (e.g. `https://ethereum.remix.org` vs `*.ethereum.org`) and never tests a same-suffix-but-different-domain attacker string, so this gap is not caught: [3](#0-2) .

### Impact Explanation
Any unprivileged, unauthenticated web attacker can register a domain that shares a trailing character sequence with an operator's configured wildcard allowlist entry (a cheap, publicly available action) and use it to host a page that issues cross-origin browser requests to the gateway's user-facing HTTP endpoint. The gateway will respond with `Access-Control-Allow-Origin` set to that attacker origin, letting the attacker's page read gateway responses in the victim's browser context that were only meant to be reachable from the legitimately allow-listed subdomains. Depending on how the browser session/token is stored and sent, this can enable cross-user response confusion or unauthorized read access to gateway JSON-RPC responses that would otherwise be restricted to trusted front-end origins.

### Likelihood Explanation
Exploitation only requires: (1) the gateway operator configuring at least one wildcard entry in `CORSAllowedOrigins` (a documented, supported feature, per [4](#0-3) ), and (2) an attacker registering an inexpensive domain whose name happens to end with the allowed suffix. No credentials, node access, or privileged position are required — the request comes from an ordinary browser hitting the internet-facing gateway HTTP server.

### Recommendation
Change the wildcard comparison to enforce a proper subdomain boundary, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
Add regression tests asserting that origins like `evil<allowedHost>` and `<random><allowedHost>` (sharing only a character suffix, not a dot-delimited subdomain relationship) are rejected.

### Proof of Concept
1. Configure the gateway with `CORSEnabled: true` and `CORSAllowedOrigins: ["https://*.ethereum.org"]`.
2. From a browser, load a page hosted at `https://evilethereum.org` (a domain the attacker can freely register) and send a cross-origin `fetch`/XHR request with header `Origin: https://evilethereum.org` to the gateway's HTTP endpoint.
3. `isAllowedOrigin` strips `*.` to get `allowedHost = "ethereum.org"`, then `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, so the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, granting the attacker page CORS access to the gateway response that should only be given to genuine `*.ethereum.org` subdomains.

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

**File:** core/services/gateway/network/httpserver_test.go (L218-231)
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
```
