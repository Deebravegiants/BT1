### Title
CORS wildcard-origin allowlist bypass via unanchored suffix matching in gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The chainlink gateway's HTTP server implements a wildcard CORS `Origin` allowlist check that matches wildcard entries (`*.example.com`) using an unanchored `strings.HasSuffix` comparison instead of verifying a proper subdomain boundary (a literal `.` immediately preceding the matched suffix, or an exact match). This lets an attacker register or control any domain that merely *ends with* the same character sequence as the allowed suffix (e.g. `evil-ethereum.org` for an allowlist entry `*.ethereum.org`) and have their `Origin` reflected back with `Access-Control-Allow-Origin`, defeating the operator's intended domain-restriction.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  parses the request's `Origin` header and each configured allowed origin into scheme/host/port, and for wildcard entries strips the `*.` prefix and does:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

There is no check that the character immediately preceding the matched suffix in `originHost` is a `.` (or that the two strings are equal). Consequently, for an allowlist entry `https://*.ethereum.org`, an origin host of `evil-ethereum.org` (which is NOT a subdomain of `ethereum.org`, but does end in the literal string `ethereum.org`) passes the check, because `strings.HasSuffix("evil-ethereum.org", "ethereum.org")` is `true`.

This is then used directly to set response headers in `handleRequest`:
```go
if s.config.CORSEnabled {
    origin := r.Header.Get("Origin")
    if s.isAllowedOrigin(origin) {
        w.Header().Set("Access-Control-Allow-Origin", origin)
        ...
``` [3](#0-2) 

The existing wildcard test suite only validates true-positive/true-negative cases with clean subdomain relationships and does not test adjacent (non-dot-separated) domains, so this gap is not caught by tests: [4](#0-3) 

This mirrors the root cause of the Traefik `SNICheck` advisory: a security-relevant allowlist/host-matching routine performs substring/suffix comparison without enforcing the domain-label boundary that wildcard matching is supposed to guarantee, letting an attacker craft a hostname that satisfies the naive string comparison while violating the intended trust boundary.

### Impact Explanation
The gateway is Chainlink's internet-facing entrypoint for external/unprivileged client requests (per [5](#0-4)  and `ProcessRequest` flow in `core/services/gateway/gateway.go`). CORS is a browser-enforced boundary that prevents an attacker-controlled web page from making credentialed cross-origin requests to the gateway on behalf of a victim's browser session. If the wildcard allowlist can be bypassed by registering a similarly-suffixed domain (e.g., `evil-ethereum.org` vs. allowed `*.ethereum.org`), an attacker-hosted page can have its origin reflected and receive permissive CORS headers, enabling cross-origin reads of gateway responses from a victim's browser context that the operator intended to restrict to legitimate subdomains. Depending on what is exposed behind the gateway path (job/handler responses, vault-related endpoints, etc.), this is a concrete allowlist-bypass / cross-user response confusion vector.

### Likelihood Explanation
Exploitability depends on an operator having configured `CORSEnabled = true` with at least one wildcard entry in `CORSAllowedOrigins` (documented/tested feature, so plausible in production) and an attacker being able to register or control a domain with the same trailing characters as the allowed suffix (e.g., buying `evilethereum.org` when `*.ethereum.org` is allowlisted). This requires no special privilege on the attacker's part beyond domain registration and getting a victim to visit an attacker page — it is reachable directly by any unauthenticated web client via the standard CORS preflight/`Origin` header flow.

### Recommendation
Fix `isAllowedOrigin` to anchor wildcard matches on a full domain-label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".example.com"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
i.e., require the matched suffix to be preceded by a literal `.`, not just be a string suffix. Add regression tests for adjacent non-dot-separated domains (e.g., `evil-ethereum.org` against `*.ethereum.org`) to prevent recurrence, mirroring the boundary-check fix applied for the analogous Traefik `SNICheck` wildcard issue.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send an HTTP request to the gateway's configured path with header `Origin: https://evil-ethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` because `strings.HasSuffix("evil-ethereum.org", "ethereum.org")` is `true`, and the response includes `Access-Control-Allow-Origin: https://evil-ethereum.org`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, even though `evil-ethereum.org` is not a subdomain of the intended `ethereum.org` domain. [6](#0-5)

### Citations

**File:** core/services/gateway/network/httpserver.go (L33-35)
```go
type HTTPRequestHandler interface {
	ProcessRequest(ctx context.Context, rawMessage []byte, auth string) (rawResponse []byte, httpStatusCode int)
}
```

**File:** core/services/gateway/network/httpserver.go (L157-202)
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
```

**File:** core/services/gateway/network/httpserver_test.go (L152-252)
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

func TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOrigin_PreflightRequest(t *testing.T) {
	t.Parallel()
	_, _, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://remix.ethereum.org", "https://another.valid.origin.com"})

	origin := "https://remix.ethereum.org"
	resp, respBytes := sendRequest(t, url, []byte("0123456789"), http.MethodOptions, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusNoContent, resp.StatusCode)
	require.Empty(t, respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))
}

func TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOrigin(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://remix.ethereum.org", "https://another.valid.origin.com"})

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin := "https://not.allowed.origin.com"
	resp, respBytes := sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Methods"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Headers"))
}

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
