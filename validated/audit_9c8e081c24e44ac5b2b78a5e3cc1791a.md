### Title
CORS origin allowlist bypass via suffix-only wildcard host matching - ([File: core/services/gateway/network/httpserver.go])

### Summary
The gateway's CORS `Origin` validation (`isAllowedOrigin`/`splitURL`) parses the attacker-controlled `Origin` header with `net/url.Parse` and matches wildcard entries (`*.example.com`) using `strings.HasSuffix` on the raw hostname, without requiring a `.` boundary before the suffix. This is the same class of bug as the reported medialize/uri.js issue (CWE-115/CWE-601 "URL confusion"): a custom, non-browser-consistent URL/host parsing routine used for a security decision produces a different (and unsafe) result than the intended authority match, letting an unprivileged network client's crafted `Origin` value be treated as if it belonged to an allow-listed domain.

### Finding Description
`isAllowedOrigin` splits both the incoming `Origin` header and each configured allowed origin into scheme/host/port via `splitURL`, which is just a thin wrapper over `url.Parse` + `net.SplitHostPort` [1](#0-0) . For wildcard entries, the code strips the `*.` prefix and then checks only `strings.HasSuffix(originHost, allowedHost)`:

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

Because `HasSuffix` does not require a `.` (or any delimiter) immediately before the matched suffix, a domain like `notethereum.org` or `evilethereum.org` matches the wildcard rule `*.ethereum.org` (stripped to `ethereum.org`) even though it is not a true subdomain of `ethereum.org`. This is a classic string-suffix hostname-matching bug, directly analogous to the reported "URL confusion" issue where a naive parser/matcher diverges from correct authority semantics and permits an attacker-controlled origin to be misclassified as trusted — the same bug class (CWE-115 misinterpretation of authority component leading to a CWE-601-style trust decision).

The origin header is fully attacker-controlled and reachable by any unauthenticated network client hitting the gateway's public HTTP endpoint (`handleRequest`), since CORS enforcement happens before any authentication step [3](#0-2) . Existing tests only exercise `ethereum.remix.org` (fails because it doesn't end with `ethereum.org`) and `another.valid.domain.org` (fails because of scheme mismatch), never testing a domain that shares only a suffix without the dot boundary (e.g. `evilethereum.org` against `*.ethereum.org`) [4](#0-3) .

### Impact Explanation
If `isAllowedOrigin` returns true for an attacker's chosen origin, the server reflects `Access-Control-Allow-Origin: <attacker origin>` and permits the associated `Access-Control-Allow-Methods`/`Headers` [5](#0-4) . A page served from an attacker-registered domain that happens to end with the allow-listed suffix (e.g. registering `evil-ethereum.org` to match `*.ethereum.org`) can then have a victim browser make cross-origin, credentialed-equivalent requests to the gateway and read the JSON-RPC responses cross-origin — a cross-user/cross-origin response confusion scenario reachable by any unprivileged external actor who can get a victim to load their page.

### Likelihood Explanation
Exploitability depends on an operator having configured at least one wildcard `CORSAllowedOrigins` entry and CORS being enabled — a supported, documented configuration path (`sample_config.toml`) [6](#0-5) . Once configured, the attacker only needs to register or control a domain name sharing the suffix and no other authentication or privilege is required, making exploitation straightforward for any external client capable of sending an HTTP request with a crafted `Origin` header.

### Recommendation
Fix the wildcard match to require a proper subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // keep leading dot: ".example.com"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` must end with `.example.com` (or equal `example.com` exactly), not merely share a character-level suffix. Add regression tests covering non-boundary suffix collisions (e.g. `evilethereum.org` vs `*.ethereum.org`) to prevent regressions.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request to the gateway's HTTP endpoint with header `Origin: https://evilethereum.org` (a domain the attacker registers/controls).
3. Observe the response contains `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, and `Access-Control-Allow-Headers: Content-Type`, exactly as it would for a legitimate `*.ethereum.org` subdomain — confirming the `strings.HasSuffix` check in `isAllowedOrigin` (core/services/gateway/network/httpserver.go:184-190) improperly classifies the untrusted origin as trusted.

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

**File:** core/scripts/gateway/sample_config.toml (L1-1)
```text
[UserServerConfig]
```
