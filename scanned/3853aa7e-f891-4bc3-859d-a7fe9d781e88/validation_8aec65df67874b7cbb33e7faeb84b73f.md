I have sufficient evidence now to confirm the vulnerability.

### Title
CORS wildcard origin matching in gateway UserServer lacks subdomain boundary check, allowing untrusted origins - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's `httpServer.isAllowedOrigin` function implements wildcard CORS origin matching (`*.domain.com`) using a plain `strings.HasSuffix` check without verifying a dot boundary between the matched suffix and the rest of the origin hostname. This is the same bug class as GHSA-v84h-653v-4pq9 (improper suffix matching in CORS origin validation): an attacker can register/control a domain that merely *ends with* the same characters as an allowed suffix (e.g. `evilethereum.org` matching allowed pattern `*.ethereum.org`), and the Gateway will incorrectly reflect `Access-Control-Allow-Origin` for that attacker-controlled origin.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  parses both the incoming request's `Origin` header and each configured allowed origin into scheme/host/port via `splitURL`. When an allowed origin uses the `*.` wildcard prefix, the code strips the `*.` and then does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
This matches any `originHost` that ends with the allowed suffix, with **no requirement that a `.` (or start-of-string) immediately precede the suffix**. So for allowed pattern `https://*.ethereum.org`, `allowedHost` becomes `ethereum.org`, and any origin host ending in the literal characters `ethereum.org` — such as `evilethereum.org`, `notethereum.org`, or attacker-registered `fakeethereum.org` — passes the check, even though it is not a subdomain of `ethereum.org` at all.

This function is invoked from `handleRequest` in [2](#0-1) , which is the HTTP handler for the Gateway's user-facing server (`UserServerConfig`), reachable directly by unprivileged external clients making requests to the Gateway's `/user` endpoint. The wildcard CORS feature is explicitly exercised and documented as supported in tests: [3](#0-2) , and `CORSAllowedOrigins` wildcard configuration is a first-class, user-settable config option (`sample_config.toml`, `sample_config_tls.toml`, integration tests).

### Impact Explanation
When a Gateway operator configures a wildcard allowed origin such as `https://*.example.com` intending to permit only genuine subdomains of `example.com`, the flawed suffix check instead allows any origin whose hostname happens to end with `example.com`, including unrelated attacker-registered domains (e.g., `evilexample.com`, `notexample.com`). Because `Access-Control-Allow-Origin` is reflected back for such origins (see `handleRequest`, lines 195-209), a malicious website hosted on such a domain can issue cross-origin, credentialed-equivalent requests (JWT/Authorization header based, per line 227-231) to the Gateway's user API and read the JSON-RPC responses, enabling cross-origin data theft / request impersonation against the Gateway API from an origin the operator never intended to trust. This matches the "allowlist bypass" / "cross-user response confusion" class called out for this bug family.

### Likelihood Explanation
Exploitation requires: (1) the Gateway operator to configure a wildcard entry in `CORSAllowedOrigins` (a documented, supported feature, not an edge case), and (2) an attacker to control or register a domain that shares the suffix string with the allowed domain (e.g., buying `evilethereum.org` when the target allows `*.ethereum.org`, or exploiting a domain that already lexically ends with the trusted suffix). Domain-suffix squatting of this kind is realistic and cheap for an attacker, and no special privilege is needed beyond hosting a web page — the victim (an unprivileged end user's browser) simply needs to visit the attacker's page while it makes cross-origin requests to the Gateway.

### Recommendation
Fix the wildcard suffix check in `isAllowedOrigin` to require a proper subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This ensures `evilethereum.org` no longer matches `*.ethereum.org`, while genuine subdomains like `foo.ethereum.org` still match.

### Proof of Concept
1. Configure Gateway `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]` (as shown in [4](#0-3) ).
2. From a browser page hosted at `https://evilethereum.org` (attacker-controlled, not a subdomain of `ethereum.org`), send a `POST` request to the Gateway's `/user` endpoint with `Origin: https://evilethereum.org`.
3. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and checks `strings.HasSuffix("evilethereum.org", "ethereum.org")`, which returns `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker page's JavaScript to read the Gateway's JSON-RPC response cross-origin, despite `evilethereum.org` not being an intended trusted origin. [5](#0-4)

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
