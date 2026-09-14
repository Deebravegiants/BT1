### Title
CORS wildcard origin allowlist bypass via missing subdomain boundary check in `isAllowedOrigin` - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Chainlink Gateway HTTP server's CORS origin validation performs wildcard host matching using `strings.HasSuffix` without verifying a `.` boundary between the attacker-controlled prefix and the allowed suffix domain. This is the same class of bug as GHSA-mpwq-j3xf-7m5w/CVE-2023-6291 — a string-based allowlist check that appears to restrict access to specific hosts but can be defeated because the matching logic does not correctly bind to the intended host structure, letting an unprivileged remote client's request be treated as if it came from an explicitly allowed origin.

### Finding Description
`isAllowedOrigin` splits the incoming `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port via `splitURL`, then compares them: [1](#0-0) 

For wildcard entries (`*.domain.com`), the code strips the `*.` prefix and then does:
```go
if strings.HasSuffix(originHost, allowedHost) {
    return true
}
```
This has no check that `originHost` has a `.` immediately preceding `allowedHost`. As a result, an attacker who controls (or registers) a domain like `evilethereum.org` sends `Origin: https://evilethereum.org`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates `true` — even though `evilethereum.org` is not a subdomain of `ethereum.org` and was never intended to be trusted by the `*.ethereum.org` allowlist entry. The scheme and port matching in the same function are exact-match and don't mitigate this, since only the host suffix check is flawed.

The existing test suite even documents the intended negative case (`https://ethereum.remix.org` correctly rejected because it doesn't end with `ethereum.org`), but does not cover the "no-dot-boundary" bypass case (`evilethereum.org`, `notarealethereum.org`, etc.): [2](#0-1) 

### Impact Explanation
When `CORSEnabled` is true and a wildcard entry is configured in `CORSAllowedOrigins`, `handleRequest` reflects the attacker's `Origin` value back in `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true: [3](#0-2) 

This lets a page hosted on a domain the operator never intended to trust (e.g., `evilethereum.org` when only `*.ethereum.org` was meant to be allowed) issue cross-origin browser requests to the Gateway's HTTP endpoint and read the JSON-RPC style response via `fetch`, bypassing the operator's explicit intent to restrict CORS to a specific set of subdomains. This is an allowlist bypass reachable by any unprivileged web attacker who can get a victim to visit a page on a similarly-suffixed domain, enabling cross-origin response disclosure for the Gateway's request/response envelope handling.

### Likelihood Explanation
The check is reachable directly from the internet-facing Gateway HTTP server whenever `CORSEnabled = true` and any wildcard entry is present in `CORSAllowedOrigins`; no special network position or credentials are required, and the exploit only requires the attacker to control (or register/host content on) a domain string that happens to end with the allowed suffix — a realistic and cheap precondition (e.g., registering `notgood-ethereum.org`).

### Recommendation
Update `isAllowedOrigin` to require a boundary check when stripping the `*.` wildcard, e.g. verify `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix`, so `evilethereum.org` is rejected while `remix.ethereum.org` still matches.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From an attacker-controlled page served at `https://evilethereum.org`, issue a `fetch` request to the Gateway endpoint with `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`, and the server reflects `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the untrusted page's JavaScript to read the response body, despite `evilethereum.org` never being an intended subdomain of `ethereum.org`.

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
