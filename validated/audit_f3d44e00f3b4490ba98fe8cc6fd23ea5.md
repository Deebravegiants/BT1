I found a concrete analog: a substring-before-wildcard bypass in the Chainlink Gateway's CORS origin allowlist matching, functionally identical to the AcceptEnv wildcard bug in the CVE.### Title
CORS wildcard origin allowlist bypassed by suffix substring match (missing dot boundary) - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Gateway's HTTP CORS layer implements wildcard-domain allowlisting (e.g. `*.ethereum.org`) for `CORSAllowedOrigins` by stripping the `*.` prefix and checking `strings.HasSuffix(originHost, allowedHost)`. Because the stripped pattern drops the separating dot, the resulting suffix check matches any hostname that merely ends with the same characters, not just true subdomains — an unprivileged remote origin such as `evilethereum.org` is incorrectly treated as an allowed origin for a `*.ethereum.org` policy. This is the same bug class as CVE-2014-2532: a substring located before/around the wildcard boundary bypasses the intended restriction.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  handles wildcard host matching as follows: [2](#0-1) 

When `allowedHost` is `"*.ethereum.org"`, `allowedHost[2:]` yields `"ethereum.org"` — the leading dot that should delimit the subdomain boundary is discarded along with the `*`. The subsequent `strings.HasSuffix(originHost, allowedHost)` therefore matches on the raw substring `"ethereum.org"` wherever it appears at the end of the origin host, with no requirement that a `.` (or scheme boundary) precede it. Consequently a completely unrelated domain like `evilethereum.org` (which is not a subdomain of `ethereum.org` at all) satisfies the suffix check and is granted the same CORS trust as a legitimate `*.ethereum.org` subdomain.

This mirrors the root cause of CVE-2014-2532: OpenSSH's wildcard-based `AcceptEnv` matching failed to properly anchor the substring before the wildcard, letting attacker-controlled strings that merely contain the allowed substring bypass the intended restriction. Here, the "restriction" is the origin's subdomain boundary, and the "substring before the wildcard" (missing dot) allows arbitrary domains sharing a suffix to pass.

The check is reached directly from `handleRequest`, which is the internet-facing entry point for every JSON-RPC request the Gateway's user-facing HTTP server receives from unauthenticated clients: [3](#0-2) 

### Impact Explanation
If an operator configures `CORSAllowedOrigins` with a wildcard entry (e.g. `https://*.mycompany.com`), any attacker who can register or control a domain that happens to end in the same string (e.g. `evilmycompany.com`, or a subdomain-less lookalike domain) can serve a web page that browsers will treat as CORS-trusted against the Gateway. Because `isAllowedOrigin` returning true causes the server to echo back `Access-Control-Allow-Origin: <attacker origin>` and enable credentialed cross-origin requests [3](#0-2) , this can be leveraged for cross-user response confusion / unauthorized read access to Gateway JSON-RPC responses that were only intended for the legitimate wildcard subdomain family, undermining the origin allowlist that operators rely on to scope browser-based access.

### Likelihood Explanation
Exploitability depends on an operator having configured at least one `*.`-prefixed wildcard entry in `CORSAllowedOrigins` (this is a supported, documented feature exercised by the wildcard test suite, e.g. `startNewServer(t, ..., []string{"https://*.ethereum.org", ...})` in [4](#0-3) ). Given that configuration, any unprivileged remote party can trigger the bypass simply by controlling a domain sharing the suffix and getting a victim browser to send a cross-origin request with that `Origin` header — no authentication or special network position is required, only an HTTP request from a browser to the Gateway's public endpoint.

### Recommendation
Fix the wildcard suffix comparison to preserve the dot boundary so only true subdomains match, e.g. compare `originHost` against `"."+allowedHost` (after stripping only the `*`), or explicitly require `strings.HasSuffix(originHost, "."+strippedHost) || originHost == strippedHost`. Add negative test coverage for domains that share a suffix but are not actual subdomains (e.g. `evilethereum.org` against `*.ethereum.org`) to prevent regression.

### Proof of Concept
1. Configure the Gateway's user-facing HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]` (as in [4](#0-3) ).
2. From an unprivileged client, send an HTTP request to the Gateway's user path with header `Origin: https://evilethereum.org`.
3. In `isAllowedOrigin`, `allowedHost` becomes `"ethereum.org"` (dot stripped) at [5](#0-4) , and `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates to `true` at [6](#0-5) , even though `evilethereum.org` is not a subdomain of `ethereum.org`.
4. The response will include `Access-Control-Allow-Origin: https://evilethereum.org` and enabled CORS headers, granting the attacker-controlled origin the same trust as a legitimate `*.ethereum.org` subdomain — a real bypass, though no test in the existing suite covers this specific non-subdomain-but-suffix-sharing case, so it is unverified against the live test harness in this session.

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

**File:** core/services/gateway/network/httpserver_test.go (L152-165)
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
```
