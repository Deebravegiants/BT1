### Title
CORS origin allowlist bypass via unanchored suffix matching enables disallowed-domain access to the Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's `httpServer.isAllowedOrigin` function validates the `Origin` header against a configured allowlist (`CORSAllowedOrigins`) using a wildcard suffix match that is not anchored to a domain-label boundary. An attacker who registers a domain that merely ends with the same characters as an allowed domain (e.g. `evilethereum.org` vs. an allowlisted `*.ethereum.org`) can get their Origin reflected back and CORS headers granted, mirroring the root cause of CVE-2023-2808 (Mattermost): a hostname/URL is judged "allowed" using a naive string comparison instead of a properly normalized/anchored comparison, letting a disallowed origin pass the check.

### Finding Description
`isAllowedOrigin` splits the incoming `Origin` header and each configured allowed origin into scheme/host/port and then does: [1](#0-0) 

```go
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
```

When `CORSAllowedOrigins` contains a wildcard entry such as `https://*.ethereum.org`, the code strips the `*.` prefix and checks only `strings.HasSuffix(originHost, "ethereum.org")`. This check has no boundary requirement (no leading `.` or exact-length check) between the attacker-controlled prefix and the trusted suffix, so any origin host that byte-for-byte ends with `ethereum.org` — including `evilethereum.org`, `notarealethereum.org`, or a domain the attacker fully owns and registers for this purpose — satisfies the match, even though it is not a subdomain of `ethereum.org` at all.

This is functionally the same bug class as CVE-2023-2808: a security-relevant allowlist decision is made from an unnormalized/unanchored string comparison of a URL/hostname, so an attacker who fully controls the crafted string can make it satisfy the check while pointing at a domain the operator never intended to trust.

The consequence in `handleRequest` is direct: if `isAllowedOrigin` returns true, the Gateway reflects the attacker's Origin back with full CORS permissions: [2](#0-1) 

### Impact Explanation
Any unprivileged network attacker who can register (or already owns) a domain sharing a suffix with an allowlisted wildcard entry can have their site's `Origin` accepted by the Gateway's CORS policy. This grants `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers` to a domain the operator explicitly did not intend to allow, enabling browser-based cross-origin requests from a malicious site to interact with the Gateway HTTP server (`ProcessRequest` handler) as if it were coming from a trusted origin. This is an allowlist bypass on an internet-facing gateway entrypoint.

### Likelihood Explanation
Exploitation only requires the attacker to control (register) any domain name string that ends with the trusted suffix — no privileged access, no credential compromise, and no interaction with legitimate users is needed beyond getting them to visit the attacker's page while their browser has access to the Gateway. Any operator that configures a wildcard CORS entry (a documented, tested pattern per `httpserver_test.go`) is exposed.

### Recommendation
Anchor the wildcard suffix match to a domain-label boundary, e.g. require `originHost == allowedHost` (post-stripping) or `strings.HasSuffix(originHost, "."+allowedHost)`, and additionally normalize hosts (IDNA/punycode, case-folding already done via lowercase) before comparison so that visually- or byte-level-similar hostnames cannot spoof the match.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled: true` and `CORSAllowedOrigins: ["https://*.ethereum.org"]`.
2. From a browser, load a page hosted at `https://evilethereum.org` (a domain fully owned by the attacker, not a subdomain of `ethereum.org`).
3. Issue a `fetch` request to the Gateway's configured path with `mode: "cors"`.
4. Observe that `isAllowedOrigin("https://evilethereum.org")` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`, and the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker's page read the Gateway's response cross-origin. [3](#0-2)

### Citations

**File:** core/services/gateway/network/httpserver.go (L180-190)
```go
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
