Audit Report

## Title
CORS wildcard origin allowlist bypass via unbounded hostname suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
`httpServer.isAllowedOrigin` implements wildcard CORS origin matching (`*.example.com`) using a bare `strings.HasSuffix(originHost, allowedHost)` check on the origin's hostname without verifying a label/dot boundary before the matched suffix. This allows any domain that merely ends with the configured suffix (e.g. `evilethereum.org` matching a `https://*.ethereum.org` allow-entry) to be treated as trusted. [1](#0-0) 

## Finding Description
`isAllowedOrigin` parses both the incoming `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port. When an allow-entry starts with `*.`, the code strips the `*.` prefix and performs `strings.HasSuffix(originHost, allowedHost)` with no dot-boundary check. [2](#0-1)  Consequently, a domain like `evilethereum.org` (attacker-registered) will pass the check for an allowlist entry of `https://*.ethereum.org`, because `"evilethereum.org"` ends with the literal string `"ethereum.org"`. The result of `isAllowedOrigin` directly gates whether `handleRequest` reflects `Access-Control-Allow-Origin` for the requesting origin. [3](#0-2) 

However, this is gated behind `CORSEnabled`, which defaults to a config the operator must explicitly set, and requires the operator to configure a wildcard allow-entry (`*.domain.tld`) in `CORSAllowedOrigins` in the first place — this is not a default-on feature and only affects operators who choose to use wildcard CORS entries. [4](#0-3) 

## Impact Explanation
This is a real logic bug: the wildcard suffix match lacks a dot-boundary check, so `evilethereum.org` would incorrectly match an allowlist entry of `*.ethereum.org`. This was confirmed directly in the code and is not present in the test suite's coverage — the existing tests (`TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards`) only test scheme/port mismatches and a non-suffix host (`ethereum.remix.org`), not the exact bypass case of a non-dotted suffix match like `evilethereum.org`. [5](#0-4) 

That said, the practical impact is bounded: exploitation requires an operator to have both (a) enabled CORS and (b) configured a *wildcard* allowed-origin entry pointing at a domain suffix that an attacker can also register a lookalike domain for (e.g., operator trusts `*.ethereum.org`, attacker registers `evilethereum.org`). This is a self-inflicted CORS misconfiguration risk contingent on the specific choice of wildcard domain and an attacker's ability to register a colliding domain name — not a vulnerability reachable against a default/unconfigured Gateway. The resulting impact (browser-based cross-origin read of JSON-RPC responses) is real but its likelihood is tied to operator-chosen wildcard domains being "guessable-suffix-collidable," which is a narrower and more configuration-dependent condition than a typical unauthenticated bypass.

## Likelihood Explanation
Exploitation requires: (1) the Gateway operator to have enabled CORS with a wildcard entry in `CORSAllowedOrigins`, and (2) the attacker to register/control a domain sharing the exact tail string of the configured suffix (not necessarily as a real subdomain). This is a non-default configuration dependency, reducing likelihood relative to an unconditional bypass, though it is trivially exploitable once such a configuration exists.

## Recommendation
Change the wildcard match to require a proper subdomain boundary, e.g. `strings.HasSuffix(originHost, "."+allowedHost)` (or equivalently `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`), so only genuine subdomains of the configured base domain are matched.

## Proof of Concept
1. Operator configures `CORSAllowedOrigins: ["https://*.ethereum.org"]` with `CORSEnabled: true`.
2. Attacker registers/controls `evilethereum.org` and serves a page from `https://evilethereum.org`.
3. Victim's browser loads the attacker page, which issues a `fetch` to the Gateway endpoint with `Origin: https://evilethereum.org`.
4. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and evaluates `strings.HasSuffix("evilethereum.org", "ethereum.org")` → `true`, so `handleRequest` sets `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker page read the Gateway's JSON-RPC response. [6](#0-5) 

A Go unit test extending `httpserver_test.go` with `startNewServer(t, ..., true, []string{"https://*.ethereum.org"})` and origin `"https://evilethereum.org"` would demonstrate `resp.Header.Get("Access-Control-Allow-Origin")` incorrectly being non-empty, confirming the bypass against the existing test harness pattern. [7](#0-6)

### Citations

**File:** core/services/gateway/network/httpserver.go (L53-54)
```go
	CORSEnabled            bool
	CORSAllowedOrigins     []string
```

**File:** core/services/gateway/network/httpserver.go (L157-209)
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
