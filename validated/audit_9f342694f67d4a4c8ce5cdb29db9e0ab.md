### Title
CORS wildcard-origin allowlist bypass via missing subdomain boundary check - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway HTTP server's CORS origin-validation logic (`isAllowedOrigin`) implements wildcard-domain matching using `strings.HasSuffix` without requiring a `.` boundary before the allowed suffix. An unprivileged, remote attacker who registers a domain that merely *ends with* the same characters as an allowed wildcard suffix (e.g. `evilethereum.org` for an allowlist entry `*.ethereum.org`) is granted `Access-Control-Allow-Origin` for that attacker-controlled origin, even though it is not a genuine subdomain. This mirrors the CVE-2016-9179 bug class: incorrect parsing/validation of the authority/host component allows a client to be tricked into trusting a different, attacker-chosen host than intended.

### Finding Description
`splitURL` parses a raw URL string and returns scheme/host/port [1](#0-0) . `isAllowedOrigin` then compares the client-supplied `Origin` header against each configured `CORSAllowedOrigins` entry. For wildcard entries (`*.domain`), it strips the `*.` prefix and checks only that the origin host has the remaining string as a suffix, with no requirement that a `.` (label boundary) precede that suffix [2](#0-1) .

Because `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, an origin such as `https://evilethereum.org` (or any domain the attacker registers ending in `ethereum.org`) will incorrectly satisfy the `*.ethereum.org` allowlist rule, despite not being a subdomain of `ethereum.org`.

This function is invoked directly on `handleRequest`, using the raw `Origin` header sent by any unauthenticated remote client hitting the gateway's internet-facing HTTP endpoint [3](#0-2) . When the check passes, the server reflects the attacker's `Origin` back in `Access-Control-Allow-Origin` and permits the corresponding cross-origin browser request/response flow [4](#0-3) .

### Impact Explanation
This is a concrete allowlist-bypass vulnerability in the gateway's origin-based access control, reachable from an unauthenticated client purely by controlling the `Origin` header/domain registration — no privileged access is required. It allows an attacker-controlled website to be treated as if it were part of the trusted wildcard domain (e.g. `*.ethereum.org`), enabling that attacker page to make cross-origin, browser-mediated JSON-RPC requests to the Gateway on behalf of a victim who visits it, and to read the CORS-exposed response — a cross-user response confusion / allowlist-bypass condition explicitly in scope.

### Likelihood Explanation
Exploitation only requires registering a domain name that happens to end with the same characters as a configured wildcard suffix (e.g. `notethereum.org`, `evilethereum.org`) and hosting a page that issues a cross-origin request to the gateway endpoint while a victim's browser has it open/visits it. No credentials, insider access, or network-level MITM capability are required, making this a low-effort, unprivileged-actor bypass of an explicit security control (the CORS allowlist).

### Recommendation
Fix the wildcard match in `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` to require a proper label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // keep the leading dot: ".ethereum.org"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` must either equal the base domain or end with `.<suffix>`, preventing domains like `evilethereum.org` from matching `*.ethereum.org`.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From an attacker-controlled browser page hosted at `https://evilethereum.org`, send a cross-origin `fetch`/XHR request to the gateway's HTTP endpoint with header `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, exactly as tested for legitimate wildcard matches in `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` [5](#0-4) , confirming the attacker's non-subdomain origin is incorrectly treated as trusted.

### Citations

**File:** core/services/gateway/network/httpserver.go (L137-155)
```go
// split URL into: scheme, hostname, port
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
