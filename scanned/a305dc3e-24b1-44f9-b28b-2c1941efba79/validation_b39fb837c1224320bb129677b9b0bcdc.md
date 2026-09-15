## Finding: CORS Origin Allowlist Bypass via Naive Suffix Matching

### Title
CORS wildcard-origin allowlist bypass via unanchored domain-suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Functions Gateway's user-facing HTTP server validates the `Origin` header against a configured CORS allowlist that supports wildcard subdomain entries (e.g. `https://*.ethereum.org`). The wildcard-matching logic strips the `*.` prefix and then performs a bare `strings.HasSuffix` comparison against the request's origin host, without requiring a `.` boundary before the matched suffix. This allows an attacker-controlled domain that merely *ends with* the allowed suffix (e.g. `evilethereum.org`) to be treated as a valid subdomain of the trusted domain (`ethereum.org`), causing the gateway to reflect `Access-Control-Allow-Origin` for an attacker's site. This mirrors the bug class in CVE-2022-0117 — a policy bypass that lets an untrusted origin obtain cross-origin access it should not have.

### Finding Description
`isAllowedOrigin` parses both the request `Origin` header and each configured allowed origin into scheme/host/port, then for wildcard entries does: [1](#0-0) 

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

If an operator configures `CORSAllowedOrigins = ["https://*.ethereum.org"]` intending to trust only genuine subdomains of `ethereum.org`, `allowedHost` becomes `ethereum.org`. Any `originHost` that ends with the literal string `ethereum.org` satisfies `HasSuffix`, including a completely unrelated domain such as `evilethereum.org` or `notethereum.org` — these are not subdomains, but the suffix check has no requirement that the preceding character be a `.`. This is the classic "unanchored suffix match" CORS/domain-validation bug class.

The result flows directly into the response headers in `handleRequest`: [2](#0-1) 

An attacker registering `evilethereum.org` and hosting a page there can issue cross-origin requests to the gateway's `/user` endpoint; the gateway will reflect `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker's page read gateway responses that browsers would otherwise block per same-origin policy — exactly the "leak cross-origin data via a crafted HTML page" bug class described in the CVE.

### Impact Explanation
This is an internet-facing component (`UserServerConfig` on the gateway, reachable by any unprivileged browser client, per `core/scripts/gateway/sample_config.toml` and the gateway integration tests using CORS-allowed origin `https://remix.ethereum.org`). An operator who intends to scope trust to `*.ethereum.org` (or any similar suffix) unintentionally admits sibling/impostor domains. This can let a malicious webpage bypass same-origin protections and exfiltrate responses returned by the gateway to a victim browser making requests to it — effectively an allowlist bypass in the internet-facing gateway's origin/authorization surface.

### Likelihood Explanation
Exploitability requires: (1) the gateway operator to configure a wildcard CORS entry (a documented/supported and reasonably common pattern, as shown in tests using `https://*.ethereum.org`), and (2) an attacker registering a domain that shares the suffix (trivially purchasable, e.g. `evilethereum.org`). No privileged access or node compromise is needed — a normal internet client crafting the right `Origin` header suffices, satisfying the "unprivileged-actor" and "remote, low-complexity" criteria.

### Recommendation
Anchor the wildcard suffix match on a domain boundary, e.g. require the origin host to equal the trusted suffix or end with `"." + allowedHost`:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
Additionally consider precomputing/normalizing the allowlist once at startup (as the existing code comment already suggests) rather than parsing on every request, and add negative test cases for sibling-suffix domains (`evilethereum.org`, `notethereum.org`) to `httpserver_test.go`.

### Proof of Concept
1. Configure gateway `UserServerConfig`:
```toml
CORSEnabled = true
CORSAllowedOrigins = ["https://*.ethereum.org"]
```
2. Send a request to the `/user` endpoint with header `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, even though `evilethereum.org` is not a subdomain of `ethereum.org` — matching the existing passing-case tests in [3](#0-2)  but with an attacker-controlled sibling domain instead of a legitimate subdomain.

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

**File:** core/services/gateway/network/httpserver.go (L195-202)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
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
