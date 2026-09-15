Audit Report

## Title
CORS wildcard-origin allowlist bypass via naive suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway's `isAllowedOrigin` function implements wildcard CORS origin matching (e.g. `*.example.com`) using a bare `strings.HasSuffix(originHost, allowedHost)` check with no domain-separator boundary validation. This allows an attacker-controlled origin such as `evilexample.com` to satisfy an allowlist entry intended only for `example.com` and its subdomains, since the string `"evilexample.com"` literally ends with the substring `"example.com"`.

## Finding Description
`isAllowedOrigin` parses the request `Origin` header and each configured `CORSAllowedOrigins` entry via `splitURL`, matching scheme and port exactly, then checking the host [1](#0-0) . For wildcard entries, it strips the `*.` prefix and performs a raw suffix comparison with no check that the match is preceded by a `.` label boundary: [2](#0-1) 

Because `strings.HasSuffix` treats the allowed host as an arbitrary trailing substring rather than a subdomain label, `strings.HasSuffix("evilexample.com", "example.com")` evaluates to `true`, letting a completely unrelated, attacker-registered domain pass an allowlist meant to restrict access to `*.example.com`. This is invoked from `handleRequest`, the single entry point for gateway HTTP traffic, which reflects the attacker's origin back in `Access-Control-Allow-Origin` once the check passes: [3](#0-2) 

Existing tests confirm the wildcard matching logic behaves exactly as described (pure suffix matching, e.g. the comment `// doesn't end with ethereum.org` in `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards`), but no test exercises the "ends-with-but-different-domain" sibling case (e.g. `evil-ethereum.org` vs `*.ethereum.org`), meaning this defect is present and unaddressed in the code as shipped: [4](#0-3) 

## Impact Explanation
This is a concrete allowlist bypass: an operator configuring `CORSAllowedOrigins = ["https://*.example.com"]` intending to restrict cross-origin access to their own subdomains instead unintentionally permits any domain that happens to end with that string (e.g. `evilexample.com`, `notexample.com`). A page hosted on such an attacker-controlled domain can issue cross-origin `fetch`/XHR requests to the gateway and read the JSON response body via the reflected `Access-Control-Allow-Origin` header [5](#0-4) . No `Access-Control-Allow-Credentials` header is set, bounding the impact to non-cookie-bearing responses, but the allowlist bypass itself is real and maps to the in-scope "allowlist bypass" / cross-origin response confusion impact class.

## Likelihood Explanation
Any unauthenticated external actor can trigger the bypass by sending a request with a crafted `Origin` header to the gateway's exposed HTTP endpoint — no credentials or special role are required for the attacker. The only precondition is that the gateway operator has configured a wildcard CORS entry, which is a normal, documented, supported configuration option (`CORSAllowedOrigins` field, exercised by existing tests), not a misuse or hardening failure on the operator's part — the flaw is inherent in the matching code regardless of which domain is chosen.

## Recommendation
Fix `isAllowedOrigin`'s wildcard branch to require the suffix be preceded by a `.` label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    baseHost := allowedHost[2:]
    if originHost == baseHost || strings.HasSuffix(originHost, "."+baseHost) {
        return true
    }
}
```
Alternatively, split both hosts on `.` and compare labels exactly rather than doing raw string suffix comparison.

## Proof of Concept
1. Configure the gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = []string{"https://*.example.com"}`.
2. Send `POST /<path>` with header `Origin: https://evilexample.com`.
3. Trace: `splitURL` yields `originHost = "evilexample.com"`; wildcard branch strips `*.` from `example.com`; `strings.HasSuffix("evilexample.com", "example.com")` returns `true` [6](#0-5) .
4. Server response includes `Access-Control-Allow-Origin: https://evilexample.com`, allowing script on `evilexample.com` to read the gateway's response cross-origin, contrary to the operator's intent to restrict to `example.com` subdomains.
5. This can be validated as a Go unit test analogous to the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`/`FromNotAllowedOriginWildcards` tests, asserting `Access-Control-Allow-Origin` is set (bypass) for origin `https://evilexample.com` against allowed origin `https://*.example.com`.

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-183)
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
