I found the vulnerability. The Gateway's HTTP server (`core/services/gateway/network/httpserver.go`) is the internet-facing user/node server for the DON, and its CORS wildcard-origin matching uses `strings.HasSuffix` without enforcing a domain-boundary (dot) check, allowing lookalike-domain bypass — the same bug class as the elysia-cors CVE (origin validated via substring/suffix match rather than exact/boundary match).

### Title
CORS wildcard origin bypass via unanchored suffix match allows lookalike-domain origin spoofing - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's `httpServer.isAllowedOrigin` function, used to enforce `CORSAllowedOrigins` on the internet-facing `UserServerConfig`/`NodeServerConfig` HTTP listeners, validates wildcard entries (e.g. `*.example.com`) by stripping the `*.` prefix and then calling `strings.HasSuffix(originHost, allowedHost)`. This check has no domain-boundary enforcement, so any origin host that merely ends with the allowed string — including a completely unrelated domain like `evilexample.com` — is accepted as if it were a legitimate subdomain of `example.com`. This mirrors the elysia-cors flaw (GHSA-f9qj-4c5x-cpcw / CVE-2025-50864), where origin validation checked for substring/suffix containment instead of an exact or properly-anchored match.

### Finding Description
`isAllowedOrigin` parses the requesting `Origin` header and each configured allowed origin, then compares scheme, port, and host: [1](#0-0) 

For exact entries it correctly requires `originHost == allowedHost`. But for wildcard entries it strips the leading `"*."` (2 characters) and then performs an unanchored suffix comparison:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
Given an operator-configured allowed origin of `*.example.com`, `allowedHost` becomes `example.com`. `strings.HasSuffix` then matches any host ending in that literal string, with no requirement that the preceding character be a `.` (subdomain separator). Consequently a host such as `evilexample.com` (12 chars ending in `example.com`) also passes the check, even though it shares no domain relationship with `example.com` at all — it is a different registrable domain that merely happens to end with the same characters.

This is called from `handleRequest`, which reflects the attacker-controlled `Origin` header back in `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true: [2](#0-1) 

This handler backs both the `UserServerConfig` and `NodeServerConfig` HTTP endpoints of the Gateway, which are the internet-facing entry points used by external clients/nodes to submit JSON-RPC requests, as configured via `CORSEnabled`/`CORSAllowedOrigins`: [3](#0-2) 

### Impact Explanation
Any operator who configures a wildcard allowed origin (a documented, supported pattern exercised in the test suite, e.g. `https://*.ethereum.org`) unintentionally also whitelists any attacker-registered domain that ends with the same suffix (e.g. `evilethereum.org`, `notethereum.org`). A page hosted on such a lookalike domain can issue cross-origin `fetch`/`XHR` requests to the Gateway's user-facing endpoint and receive the reflected `Access-Control-Allow-Origin` header, letting the browser expose the JSON-RPC response to attacker-controlled script. This breaks the operator's intended origin allowlist and enables unauthorized cross-origin reads of Gateway responses from a domain never actually authorized, i.e., an allowlist bypass on an internet-facing component.

### Likelihood Explanation
Exploitability requires only that the Gateway operator has configured `CORSEnabled = true` with at least one wildcard entry in `CORSAllowedOrigins` — a pattern explicitly supported and tested by the codebase's own wildcard test cases: [4](#0-3) . No privileged access or special conditions are needed by the attacker beyond registering/controlling a domain that shares the allowed suffix; the flaw is purely in the string-comparison logic and is deterministically triggered for any qualifying origin.

### Recommendation
Anchor the wildcard suffix match on a domain boundary instead of a raw string suffix, e.g. require that the origin either equals the base domain or ends with `"." + allowedHost`:
```go
if strings.HasPrefix(allowed, "*.") {
    base := allowedHost // after stripping "*."
    if originHost == base || strings.HasSuffix(originHost, "."+base) {
        return true
    }
}
```
This ensures `evilexample.com` (no separating dot) is rejected while legitimate subdomains like `sub.example.com` continue to match.

### Proof of Concept
1. Configure the Gateway's `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.example.com"]`.
2. From a browser page hosted at `https://evilexample.com`, send `fetch("https://gateway-host/user", { method: "POST", headers: {"Origin": "https://evilexample.com"} })`.
3. Observe that `isAllowedOrigin` returns `true` (since `"evilexample.com"` ends with `"example.com"`), and the response includes `Access-Control-Allow-Origin: https://evilexample.com`, letting the attacker's page read the Gateway's response cross-origin despite `evilexample.com` never being an intended subdomain of `example.com`. [5](#0-4)

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

**File:** core/scripts/gateway/sample_config_tls.toml (L12-13)
```text
CORSEnabled = false
CORSAllowedOrigins = []
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
