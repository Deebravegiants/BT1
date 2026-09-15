The code exactly matches the claim: `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` performs an unanchored `strings.HasSuffix(originHost, allowedHost)` check for wildcard entries with no boundary/delimiter validation.Audit Report

## Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements wildcard CORS origin matching (`*.domain.com`) using an unanchored `strings.HasSuffix(originHost, allowedHost)` check with no delimiter/boundary validation. An operator-configured wildcard entry like `*.remix.com` is therefore satisfied by any hostname that merely ends with the literal string `remix.com`, such as `evilremix.com`, which is not a subdomain of `remix.com` at all. [1](#0-0) 

## Finding Description
The function splits the request's `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port and checks scheme, port, exact-host match, then falls through to wildcard matching: for entries prefixed with `*.`, it strips the prefix and does a bare `strings.HasSuffix(originHost, allowedHost)` with no check that the character preceding the matched suffix in `originHost` is a `.` (or that `originHost` is empty before it). [2](#0-1)  This is invoked unconditionally from `handleRequest`, which is the handler bound to the gateway's public, unauthenticated HTTP path for every incoming request, before any body-size limiting or JWT extraction occurs: [3](#0-2)  No authentication gates reaching `isAllowedOrigin`; only the `Origin` header on the request is used. The repository's own test suite confirms wildcard patterns like `*.ethereum.org` are a supported, intended configuration (`TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`) and that the negative test cases only check unrelated-scheme/port/non-suffix examples (`ethereum.remix.org`, `http://` vs `https://`, missing port) — none of the existing tests cover a suffix-collision case like `evilethereum.org` against `*.ethereum.org`, so the bug is not caught or acknowledged by the test suite. [4](#0-3) 

## Impact Explanation
When `CORSEnabled=true` and a wildcard entry is configured, an attacker who registers a domain sharing only a string suffix with the allowed domain (e.g. `evilremix.com` vs. allowed `*.remix.com`) can have their `Origin` reflected into `Access-Control-Allow-Origin`, plus `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`, effectively being treated as a trusted subdomain by the browser's CORS enforcement. This is a genuine allowlist-boundary bug in the gateway's CORS logic and matches the in-scope "allowlist bypass" impact category. However, this CORS check only controls whether a browser will expose cross-origin *response* contents to JavaScript on the attacker's page — it does not bypass the underlying JWT/bearer-token authentication performed by `HTTPRequestHandler.ProcessRequest`, nor does it grant the attacker any capability beyond what an unauthenticated request to the gateway path already allows (the gateway path handles unauthenticated inbound requests by design, per `jwtToken` being optional in `handleRequest`). The severity is real but bounded: it primarily affects browser-based cross-origin read access to whatever unauthenticated gateway responses reveal, not fund movement, key exfiltration, or authentication bypass.

## Likelihood Explanation
Exploitability requires: (1) the operator enables `CORSEnabled=true`, and (2) configures at least one wildcard `CORSAllowedOrigins` entry — both are documented, supported configuration options exercised in this repo's own tests. Given those preconditions, any attacker can register a domain with the matching suffix and send a crafted `Origin` header with no privileged access, matching an unprivileged-client threat model.

## Recommendation
Anchor the wildcard suffix comparison to a subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This preserves matching for genuine subdomains (`api.remix.com`) while rejecting suffix-collision domains (`evilremix.com`).

## Proof of Concept
1. Start the gateway HTTP server with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.remix.com"}` (as in `startNewServer` in `httpserver_test.go`).
2. Send a POST request to the configured path with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type` — confirming the non-subdomain `evilremix.com` is incorrectly treated as matching `*.remix.com`.
4. This can be codified as a new unit test in `core/services/gateway/network/httpserver_test.go` analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards`, asserting `Access-Control-Allow-Origin` is empty for origin `https://evilremix.com` against allowed `https://*.remix.com` — which currently fails against the vulnerable code.

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
