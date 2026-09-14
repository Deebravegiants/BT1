## Analog Vulnerability Found

### Title
CORS Wildcard Origin Allowlist Bypass via Unanchored Suffix Match - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's user-facing HTTP server validates the `Origin` header against a configured CORS allowlist using a wildcard match that is implemented with a plain `strings.HasSuffix` check instead of a domain-boundary-aware comparison. This allows an unprivileged, internet-facing attacker who registers a domain that merely *ends with* the configured suffix (not an actual subdomain) to be treated as an allowed origin, echoing that attacker's `Origin` back in `Access-Control-Allow-Origin` and exposing gateway response data to a host the operator never intended to trust — the same class of bug as CVE-2019-9636 (URL/host component incorrectly resolved, causing data to be released to the wrong host).

### Finding Description
`isAllowedOrigin` splits both the incoming `Origin` header and each configured allowlist entry into scheme/host/port via `splitURL`, then for wildcard entries (`*.example.com`) strips the `*.` prefix and checks: [1](#0-0) 

`strings.HasSuffix(originHost, allowedHost)` has no boundary check for the character immediately preceding the matched suffix. So for a configured wildcard `*.ethereum.org` (intended to match `foo.ethereum.org`, `bar.ethereum.org`, etc.), an attacker-registered domain such as `evilethereum.org` or `xethereum.org` also satisfies `HasSuffix("evilethereum.org", "ethereum.org") == true`, even though it is a completely unrelated, attacker-controlled registrable domain and not a subdomain of `ethereum.org` at all.

This allowlist result is used directly to set CORS response headers on the gateway's public user-facing HTTP server: [2](#0-1) 

This server is the internet-facing gateway endpoint that processes JSON-RPC requests (`ProcessRequest`), i.e. reachable by any unprivileged client, matching the "internet-facing gateway ... allowlist/subscriptions" scope in the analog rules.

### Impact Explanation
An attacker who registers a domain string ending in an operator-configured wildcard suffix (e.g. `evil` + `ethereum.org`) can host a malicious webpage that issues cross-origin `fetch`/`XHR` requests to the gateway. Because `Access-Control-Allow-Origin` will be set to the attacker's origin, the browser will expose the gateway's JSON-RPC response (job/workflow results, capability responses, etc.) to attacker-controlled JavaScript — cross-origin response confusion / information disclosure to an unintended host, without requiring any privileged access, matching the "cross-user response confusion" / disclosure criteria in the validation rules.

### Likelihood Explanation
Exploitation only requires: (1) the gateway operator has configured a wildcard CORS entry (a documented, supported feature per `sample_config.toml`), and (2) the attacker registers/controls any domain name that textually ends with the configured suffix — a low-cost, entirely self-serve action requiring no privileged access to Chainlink infrastructure. The existing test suite only validates *legitimate* subdomain cases and near-miss non-matches (different scheme/port, no shared suffix); it does not test the suffix-without-dot-boundary case, so the bug is unguarded in both code and tests: [3](#0-2) 

### Recommendation
Change the wildcard comparison in `isAllowedOrigin` to require a literal `.` boundary before the matched suffix (e.g. check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`), or parse both hosts into labels and compare the trailing label sequence rather than doing a raw string suffix match.

### Proof of Concept
1. Gateway operator configures `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers `https://evilethereum.org` and hosts a page there.
3. Victim visits the attacker page; it performs `fetch("https://gateway-host/", {method: "POST", ...})` with `Origin: https://evilethereum.org`.
4. Server code at [4](#0-3)  evaluates `strings.HasSuffix("evilethereum.org", "ethereum.org")` → `true`, so `isAllowedOrigin` returns `true`.
5. Server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, and the attacker's JavaScript can read the JSON-RPC response body.

### Citations

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

**File:** core/services/gateway/network/httpserver_test.go (L218-251)
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
```
