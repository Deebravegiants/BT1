### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's internet-facing HTTP server implements its own CORS origin-matching logic instead of relying on a vetted CORS library. The wildcard-matching branch of `isAllowedOrigin` strips the `*.` prefix from a configured allowed origin and then checks `strings.HasSuffix(originHost, allowedHost)` with no boundary/dot check before the suffix. This reproduces the exact bug class described in GHSA-869c-j7wc-8jqv (Gin CORS `parseWildcardRules` wildcard mishandling): a hostname that merely *ends with* the intended domain string — but is not actually a subdomain of it — is incorrectly treated as an allowed origin.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  parses both the request `Origin` header and each configured allowed origin into scheme/host/port via `splitURL`, requires exact scheme and port match, then does:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

This is a raw suffix check with no requirement that the character immediately preceding the matched suffix be a `.` (subdomain delimiter). Consequently, for a configured allowlist entry such as `https://*.ethereum.org`, the stripped comparison string becomes `ethereum.org`, and any origin host that ends with the literal bytes `ethereum.org` — including unrelated domains like `evilethereum.org`, `notethereum.org`, or `attacker-ethereum.org` — passes the check, even though none of these are subdomains of `ethereum.org`. This mirrors the CVE example of `http://localhost.example.com` being wrongly accepted when only `http://localhost` should be, and `https://example.community` matching a `https://example.com` wildcard rule.

This logic feeds directly into `handleRequest`: [2](#0-1) , which sets `Access-Control-Allow-Origin` to the (attacker-controlled) `Origin` header value whenever `isAllowedOrigin` returns true, with no additional validation.

### Impact Explanation
Any unprivileged, unauthenticated web attacker who registers a domain that happens to end with the same substring as an operator's intended wildcard suffix (e.g. registering `evil-ethereum.org` to bypass an allowlist entry of `https://*.ethereum.org`) can get the Gateway to reflect their origin in `Access-Control-Allow-Origin`. Browsers of victims who visit the attacker's page while authenticated/interacting with the Gateway API would then allow cross-origin XHR/fetch responses to be read by the attacker's page, defeating the same-origin protection the allowlist is meant to enforce. Depending on what capabilities are exposed behind this Gateway endpoint (job/DON requests, node interactions), this can lead to unauthorized cross-origin request/response access — a CORS/allowlist bypass consistent with the CWE-346 classification of the underlying advisory.

### Likelihood Explanation
Exploitability depends entirely on operator configuration: the bug is only reachable if the operator configures a wildcard entry in `CORSAllowedOrigins` (e.g., `https://*.ethereum.org`), which is an explicitly supported and tested configuration pattern (see `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` in [3](#0-2) ). Given that wildcard subdomain allowlisting is a documented, supported feature, and domain registration to craft a matching suffix is trivial and requires no privileges, likelihood is meaningful wherever this configuration option is used in production.

### Recommendation
Fix the wildcard suffix comparison to enforce a subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    base := allowedHost[2:]
    if originHost == base || strings.HasSuffix(originHost, "."+base) {
        return true
    }
}
```
This ensures `evilethereum.org` no longer matches `*.ethereum.org`, while `foo.ethereum.org` still correctly matches. Add regression tests covering suffix-but-not-subdomain hostnames (e.g. `evil-ethereum.org`, `notethereum.org`) to prevent regressions.

### Proof of Concept
1. Operator configures Gateway with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.ethereum.org"}`.
2. Attacker registers/controls `https://evilethereum.org` and hosts a malicious page there.
3. A victim's browser (already interacting with the Gateway, e.g. via cookies/session) loads the attacker page, which issues a `fetch`/`XHR` request to the Gateway with `Origin: https://evilethereum.org`.
4. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and evaluates `strings.HasSuffix("evilethereum.org", "ethereum.org")`, which is `true`.
5. The Gateway responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker's page to read the cross-origin response, despite `evilethereum.org` not being a subdomain of the intended `ethereum.org`. [4](#0-3)

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
