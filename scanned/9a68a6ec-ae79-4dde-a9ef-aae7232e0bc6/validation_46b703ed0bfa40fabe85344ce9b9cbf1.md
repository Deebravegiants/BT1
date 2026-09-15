## Title
CORS `isAllowedOrigin` origin-allowlist check permits domains with only a partial suffix match, bypassing wildcard restrictions - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The gateway's user-facing HTTP server (`UserServerConfig` / `httpServer.handleRequest`) validates the `Origin` header against an operator-configured `CORSAllowedOrigins` allowlist via `isAllowedOrigin`. For wildcard entries (e.g. `https://*.ethereum.org`), the match is performed with `strings.HasSuffix(originHost, allowedHost)` after stripping the `*.` prefix, with no check that the character immediately preceding the matched suffix is a `.` separator. This is the exact bug class described in the OIDC advisory (CWE-20, improper domain-suffix validation): a request `Origin` such as `https://evilethereum.org` will satisfy `HasSuffix("evilethereum.org", "ethereum.org")` even though it is not a subdomain of the allowed domain.

### Finding Description [1](#0-0) 

```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	originScheme, originHost, originPort, err := s.splitURL(origin)
	...
	for _, allowed := range s.config.CORSAllowedOrigins {
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
		...
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

When a `*.domain.com` wildcard entry is configured, the code strips the `*.` and then checks only `strings.HasSuffix(originHost, allowedHost)`. This is a pure string-suffix comparison with no boundary check for a preceding `.`. As a result, any attacker-registered domain that ends with the same characters as the allowed domain — without actually being a subdomain (e.g. `evilethereum.org` vs. the allowed `*.ethereum.org`) — is treated as an allowed origin. This mirrors the root cause of CVE-2024-27918, where a suffix-only comparison (`strings.HasSuffix`) let `user@exploitcorp.com` satisfy an allowlist for `corp.com`.

This check is invoked from `handleRequest`, the entry point that processes every unprivileged, internet-facing request to the gateway's `UserServerConfig` HTTP endpoint: [2](#0-1) 

The existing test suite only verifies non-matching suffix cases that don't share a common suffix boundary at all (e.g. `https://ethereum.remix.org` vs `*.ethereum.org`), so it does not cover this specific "attacker domain ends with allowed suffix but has no dot boundary" scenario: [3](#0-2) 

### Impact Explanation
An operator who configures a wildcard `CORSAllowedOrigins` entry (a supported and documented pattern, e.g. `["https://*.ethereum.org", ...]` as used in the gateway's own integration test config) intends to restrict cross-origin access to that specific domain family. Due to the suffix-only match, any attacker who registers a look-alike domain (e.g. `evil-ethereum.org`, `notethereum.org`) can serve a malicious web page from that domain, have it pass the `isAllowedOrigin` check, and receive `Access-Control-Allow-Origin` reflecting their attacker-controlled origin. This lets a third-party site issue cross-origin JSON-RPC requests to the gateway's user endpoint and read the responses in-browser, which the operator explicitly intended to prevent by scoping the wildcard. This is a genuine allowlist-bypass in the internet-facing gateway consistent with the requested bug class.

### Likelihood Explanation
Exploitation only requires registering a domain string that happens to end with the configured allowed suffix (no special access, no compromise of any node/peer, purely an unprivileged web client interacting with the public-facing gateway endpoint) — directly analogous to the ease of exploitation in the original OIDC advisory (registering `exploitcorp.com` to satisfy `corp.com`).

### Recommendation
Change the wildcard match to require a dot boundary, e.g.:
```go
if strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost {
    return true
}
```
This ensures only genuine subdomains of the allowed domain match, closing the suffix-confusion bypass.

### Proof of Concept
1. Gateway operator configures `CORSAllowedOrigins = ["https://*.ethereum.org"]` for the `UserServerConfig` endpoint (pattern shown in `core/services/gateway/integration_tests/gateway_integration_test.go` and `core/scripts/gateway/sample_config_tls.toml`).
2. Attacker registers `evilethereum.org` and serves a page from `https://evilethereum.org`.
3. Attacker's page issues a cross-origin `fetch()`/XHR to the gateway's `/user` endpoint with `Origin: https://evilethereum.org`.
4. `isAllowedOrigin` strips `*.` from `ethereum.org` and evaluates `strings.HasSuffix("evilethereum.org", "ethereum.org")`, which returns `true`.
5. The server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker's script to read the JSON-RPC response, despite `evilethereum.org` not being a legitimate subdomain of `ethereum.org`.

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

**File:** core/services/gateway/network/httpserver_test.go (L218-232)
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
