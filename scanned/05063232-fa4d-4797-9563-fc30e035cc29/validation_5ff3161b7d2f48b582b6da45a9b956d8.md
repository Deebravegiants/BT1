### Title
Gateway CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The Chainlink Gateway's internet-facing HTTP server implements a CORS allowlist that supports wildcard entries like `*.example.com`. The wildcard match strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` without verifying that the matched suffix is preceded by a literal `.` (label boundary). This causes any origin whose hostname merely *ends with* the allowed suffix string — not just true subdomains — to be treated as an allowed origin, mirroring the root cause of the referenced authentik CVE-2024-52289 (unanchored, loosely-escaped matching that lets an attacker-controlled domain satisfy an intended-narrow allowlist check).

### Finding Description
`isAllowedOrigin` in [1](#0-0)  iterates configured `CORSAllowedOrigins` and, for wildcard entries, does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

For an operator configuration of `*.remix.com` (intended to allow only hosts like `foo.remix.com`), `allowedHost` becomes `remix.com`, and the check becomes `strings.HasSuffix(originHost, "remix.com")`. This matches any hostname ending in the literal string `remix.com` with no dot boundary check, so an attacker who registers `evilremix.com` (no dot between `evil` and `remix.com`) satisfies the suffix check and is treated as an allowed subdomain, even though it is not a subdomain of `remix.com` at all.

This directly parallels the authentik bug class: a "should only match a specific domain/subdomain pattern" check is implemented with a naive string operation (there: unescaped regex; here: unanchored suffix match) that fails to enforce the label/domain boundary, letting an attacker-registered domain slip through validation.

This function is invoked from `handleRequest`, which is the primary entry point for all inbound HTTP requests to the Gateway server: [3](#0-2) . Any unauthenticated external client can send a request with an arbitrary `Origin` header and, if that origin's hostname happens to share the configured wildcard suffix as a substring, receive `Access-Control-Allow-Origin` echoing their attacker-controlled origin.

### Impact Explanation
When an operator configures a wildcard CORS allowlist (e.g., `*.mycompany.com`) intending to scope access to their own subdomains, an attacker who registers a look-alike domain ending in the same characters (e.g., `evilmycompany.com`, or more plausibly a domain like `notmycompany.com`) can have their site's cross-origin requests to the Gateway treated as trusted. The server responds with `Access-Control-Allow-Origin: <attacker origin>`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, permitting the attacker's page (via victim browsers) to make credentialed/authenticated cross-origin requests to the Gateway and read the JSON responses (e.g., job/workflow gateway API responses), which is a cross-origin allowlist bypass leading to request impersonation / response confusion for gateway API traffic.

### Likelihood Explanation
Exploitation only requires the attacker to register a domain string containing the allowed suffix as a trailing substring (no special TLD control or privileged position needed) and to lure a victim (whose browser has access/credentials to the Gateway) to visit it. No compromise of Chainlink infrastructure, no privileged role, and no code path beyond a normal HTTP request with a crafted `Origin` header is required, making this reachable directly by an unprivileged external actor against the gateway's public HTTP endpoint.

### Recommendation
Change the wildcard match to require a `.`-anchored boundary, e.g. check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of the bare `strings.HasSuffix(originHost, allowedHost)`, so `evilmycompany.com` is rejected while `sub.mycompany.com` is still accepted. Add regression tests analogous to the existing wildcard tests in [4](#0-3)  that specifically assert rejection of hostnames sharing only a trailing-substring match without a dot boundary.

### Proof of Concept
1. Configure the Gateway with `CORSAllowedOrigins = ["https://*.remix.com"]` and `CORSEnabled = true`.
2. From a browser/script, send a request to the Gateway's HTTP endpoint with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type` — despite `evilremix.com` not being a subdomain of `remix.com` — because `isAllowedOrigin` at [5](#0-4)  only checks `strings.HasSuffix("evilremix.com", "remix.com")`, which is `true`.

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

**File:** core/services/gateway/network/httpserver_test.go (L218-252)
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
}
```
