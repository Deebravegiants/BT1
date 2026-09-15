Audit Report

## Title
CORS wildcard-origin allowlist bypass via missing subdomain boundary check - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway's `isAllowedOrigin` function matches wildcard CORS origins (e.g. `*.ethereum.org`) using a raw `strings.HasSuffix` comparison without verifying a proper subdomain boundary (a preceding `.`). An attacker who registers a domain that shares the configured suffix as a bare string (e.g. `evilethereum.org` against wildcard `*.ethereum.org`) can pass the check and have the gateway reflect their origin into `Access-Control-Allow-Origin`, granting unintended cross-origin access.

## Finding Description
`splitURL` parses the scheme/host/port from a raw origin URL [1](#0-0) . `isAllowedOrigin` then compares the parsed origin host against each `CORSAllowedOrigins` entry; for wildcard entries it strips the `*.` prefix and performs `strings.HasSuffix(originHost, allowedHost)` without checking that the matched suffix begins at a `.` boundary [2](#0-1) . As a result, `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, incorrectly treating an unrelated domain as a valid subdomain of the configured wildcard.

This function is invoked on every request to the gateway's user-facing HTTP endpoint when `CORSEnabled` is true, and directly reflects the raw `Origin` header value into the `Access-Control-Allow-Origin` response header on a match, before the request body is even read or forwarded to `s.handler.ProcessRequest` [3](#0-2) . No authentication or special role is required to send this request — any browser client reaching the gateway's endpoint with a crafted `Origin` header triggers the check.

The existing test suite for wildcard matching only exercises the correct-accept cases (`remix.ethereum.org` matching `*.ethereum.org`) [4](#0-3)  and the case where the origin doesn't share the suffix at all (`ethereum.remix.org` vs `*.ethereum.org`) [5](#0-4) . It does not test the boundary-confusion case (`evilethereum.org` vs `*.ethereum.org`), so this bypass is unguarded by tests and reproducible against the current code.

## Impact Explanation
When a gateway operator configures a wildcard CORS entry — a supported configuration pattern demonstrated by the existing test suite — an attacker who registers a domain sharing the wildcard suffix without a dot boundary can serve a page from that domain and receive `Access-Control-Allow-Origin` matching their controlled origin. This lets a victim's browser visiting that page make credentialed cross-origin requests to the gateway and read responses (e.g., JSON-RPC data relayed from DON nodes) that should be restricted to legitimate configured subdomains, which is a concrete cross-origin/cross-user response exposure caused directly by the flawed matching logic in this file, not by misuse of the feature.

## Likelihood Explanation
Exploitation requires only (1) `CORSEnabled = true` with a wildcard entry in `CORSAllowedOrigins`, both being intended, supported configuration options rather than accidental misconfiguration, and (2) the attacker registering a cheap domain matching the suffix pattern. No Chainlink credential, role, or node/operator access is needed to send the triggering request — the `Origin` header is fully attacker-controlled and evaluated on every request.

## Recommendation
Require a true label boundary in the suffix check, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
Add a regression test asserting `https://evilethereum.org` is rejected against allowlist entry `https://*.ethereum.org`.

## Proof of Concept
1. Start the gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = []string{"https://*.ethereum.org"}` (mirrors `startNewServer` in `httpserver_test.go`).
2. Send a request to the gateway's configured path with header `Origin: https://evilethereum.org`.
3. Observe `isAllowedOrigin` returns `true` via `strings.HasSuffix("evilethereum.org", "ethereum.org")`, and the response contains `Access-Control-Allow-Origin: https://evilethereum.org` — the same assertion pattern used in `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` [6](#0-5) , but for a non-subdomain, attacker-controlled origin.

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
