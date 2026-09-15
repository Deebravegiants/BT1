## Analysis Result

I found a genuine analog: a host-validation boundary bug in the gateway's CORS origin allowlist matching, in the same bug class as CVE-2022-27780 (URL/host parser incorrectly treats a crafted string as matching the intended host, letting an attacker-controlled string satisfy a trust boundary check).

### Title
CORS wildcard-origin allowlist bypass via missing subdomain boundary check - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's `isAllowedOrigin` function matches wildcard CORS origins (e.g. `*.ethereum.org`) using a raw string `strings.HasSuffix` check instead of validating a proper label/domain boundary (`.`) before the suffix. An unprivileged, unauthenticated browser client can send an `Origin` header such as `https://evilethereum.org`, which passes the suffix check against configured wildcard entry `*.ethereum.org`, causing the gateway to reflect the attacker-controlled origin back in `Access-Control-Allow-Origin` and permit cross-origin, credentialed browser requests that should have been rejected.

### Finding Description
`splitURL` parses a URL and extracts scheme/host/port [1](#0-0) . `isAllowedOrigin` then compares an incoming `Origin` header's host against each configured allowed origin. For wildcard entries, it strips the `*.` prefix and does:

```go
if strings.HasSuffix(originHost, allowedHost) {
    return true
}
``` [2](#0-1) 

This is a raw string suffix comparison with no check that the character immediately preceding the matched suffix is a `.` (i.e., a true subdomain boundary). Consequently, given a configured wildcard origin `https://*.ethereum.org`, an origin value of `https://evilethereum.org` — a completely different, attacker-registrable domain — satisfies `HasSuffix("evilethereum.org", "ethereum.org")` and is treated as allowed.

This function is invoked directly on every request to the gateway's user-facing HTTP server when CORS is enabled, from `handleRequest`, which reflects the raw `Origin` header value into `Access-Control-Allow-Origin` on a match: [3](#0-2) . This is the internet-facing gateway entry point reachable by any unprivileged client (`handleRequest` processes the raw HTTP request body and forwards it to `s.handler.ProcessRequest` after the CORS check) [4](#0-3) .

The existing test suite only validates the negative case where the origin doesn't share the suffix at all (`ethereum.remix.org` vs `*.ethereum.org`) [5](#0-4) ; it does not cover the boundary-confusion case (`evilethereum.org` vs `*.ethereum.org`), so the bypass is untested and unguarded.

This is directly analogous to the curl CVE-2022-27780 bug class: a parser/matcher accepts a crafted value that superficially resembles the trusted host/domain but is actually a different, attacker-controlled entity, because a required delimiter/boundary check is missing.

### Impact Explanation
If the gateway operator configures a wildcard CORS allowlist entry (a supported and documented configuration pattern, as shown by the wildcard test cases), an attacker who registers a domain sharing the configured suffix as a bare string (e.g. `evil` + `ethereum.org` = `evilethereum.org`) can serve a malicious web page from that domain. A victim's browser visiting that page can make cross-origin requests to the gateway's user-facing endpoint, and the gateway will respond with CORS headers granting that origin access, enabling the malicious site to read gateway responses that should be restricted to the legitimately allowed subdomains (e.g., authenticated JSON-RPC responses relayed from DON nodes). This is a cross-user/cross-origin response confusion and allowlist-bypass primitive triggered entirely by an unprivileged external actor.

### Likelihood Explanation
Exploitation only requires: (1) a gateway deployment with `CORSEnabled = true` and at least one wildcard entry in `CORSAllowedOrigins`, and (2) registering/controlling a domain that shares the wildcard's suffix without the dot boundary (a cheap, unprivileged action, e.g. registering `evil<suffix>.org`/`.com` style domains). No authentication or insider access is needed to trigger the check — it is evaluated on every incoming request's `Origin` header.

### Recommendation
Fix the suffix comparison in `isAllowedOrigin` to require a true subdomain boundary, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
Add a regression test asserting that an origin like `https://evilethereum.org` is rejected against an allowlist entry `https://*.ethereum.org`.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request to the gateway's user HTTP endpoint with header `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` (via `strings.HasSuffix("evilethereum.org", "ethereum.org")`), and the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, granting the attacker-controlled origin CORS access — reproducing the same code path exercised (but not negatively tested for this case) in `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` [6](#0-5) .

### Citations

**File:** core/services/gateway/network/httpserver.go (L138-155)
```go
func (s *httpServer) splitURL(rawURL string) (string, string, string, error) {
	// lowercase the URL to avoid case sensitivity issues
	parsedURL, err := url.Parse(strings.ToLower(rawURL))
	if err != nil {
		return "", "", "", fmt.Errorf("error parsing URL: %w", err)
	}

	host, port, err := net.SplitHostPort(parsedURL.Host)
	if err != nil {
		// if there's no port, the host itself is returned
		if parsedURL.Host != "" {
			return parsedURL.Scheme, parsedURL.Host, "", nil
		}
		return "", "", "", fmt.Errorf("error splitting host and port: %w", err)
	}

	return parsedURL.Scheme, host, port, nil
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

**File:** core/services/gateway/network/httpserver.go (L211-234)
```go
	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
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
