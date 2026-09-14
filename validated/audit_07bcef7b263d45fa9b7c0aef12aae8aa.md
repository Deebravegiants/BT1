### Title
CORS wildcard-origin allowlist bypass via missing domain-boundary check enables cross-origin response disclosure - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's internet-facing HTTP server validates the `Origin` header against a configured allowlist to decide whether to reflect `Access-Control-Allow-Origin`. Wildcard entries such as `https://*.ethereum.org` are matched using a plain `strings.HasSuffix` check with no domain-boundary (dot) validation, so any origin that merely ends with the configured suffix — not just true subdomains — is accepted, analogous to the WebKit Same-Origin-Policy bypass in CVE-2017-2364 where a crafted site could obtain cross-origin data it should not have access to.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  performs the wildcard match as:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
This checks only that `originHost` ends with the configured suffix string, without requiring a `.` (or exact host boundary) immediately preceding it. Consequently, for an allowlist entry `https://*.ethereum.org`, an attacker-registered origin such as `https://evilethereum.org` (no dot before `ethereum.org`) satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org")` and is treated as an allowed subdomain, even though it is an entirely unrelated domain.

`handleRequest` at [2](#0-1)  reflects the attacker's `Origin` value back in `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true, allowing the browser to expose the cross-origin response body to script running on the attacker's page — the same class of impact described in CVE-2017-2364 (SOP bypass allowing a crafted site to read cross-origin data).

The existing test suite only validates the positive (`https://remix.ethereum.org` matches `*.ethereum.org`) and negative "different suffix" cases (`https://ethereum.remix.org` vs `*.ethereum.org`) in [3](#0-2) ; it never exercises a same-suffix-but-different-domain probe like `evilethereum.org`, so the boundary-check gap is untested and unnoticed.

### Impact Explanation
This is the gateway's public-facing HTTP endpoint (`HTTPServer`/`handleRequest`), reachable by any unprivileged remote client. If CORS is enabled with a wildcard allow-origin config (a supported, documented feature — see `sample_config.toml`/`sample_config_tls.toml`), an attacker who registers a domain sharing the configured suffix (e.g. `evilethereum.org` vs. allowed `*.ethereum.org`) can have their page's cross-origin requests treated as if they came from a trusted subdomain. Combined with `Access-Control-Allow-Headers: Content-Type` reflecting the attacker's origin, this allows a malicious website to read gateway JSON-RPC responses (which may include vault/secrets or workflow data returned to that request) that the CORS policy was intended to keep restricted to the operator's legitimate UI domains — a cross-user/cross-origin response confusion.

### Likelihood Explanation
Exploitation requires: (1) the operator enabling CORS with a wildcard suffix rule (a supported configuration pattern shown in sample configs), and (2) the attacker registering or controlling a domain that shares the suffix string without a subdomain boundary (e.g., buying `evilethereum.org` to abuse an `*.ethereum.org` rule). This is a realistic and low-cost attack for any operator using wildcard CORS entries, though it does not affect operators who only use exact-origin allowlists.

### Recommendation
Fix the wildcard match to require a proper subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` must equal the base domain or end with `.` + base domain, rejecting look-alike domains such as `evilethereum.org`.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser page hosted at `https://evilethereum.org`, send a `fetch` request with `Origin: https://evilethereum.org` to the gateway's HTTP endpoint.
3. `isAllowedOrigin` computes `originHost = "evilethereum.org"`, `allowedHost` (after stripping `*.`) = `"ethereum.org"`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker page read the JSON-RPC response body via the browser's Fetch API — despite `evilethereum.org` never being an intended subdomain of `ethereum.org`.

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

**File:** core/services/gateway/network/httpserver_test.go (L152-251)
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
```
