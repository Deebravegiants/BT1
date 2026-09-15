### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's user-facing HTTP server implements a custom CORS allowlist check that supports `*.domain.com`-style wildcard entries in `CORSAllowedOrigins`. The wildcard match uses a plain string-suffix comparison instead of verifying a subdomain (dot) boundary, allowing origins that merely end with the same characters — not actual subdomains — to be treated as trusted and receive `Access-Control-Allow-Origin` echoing the attacker-controlled `Origin` header.

### Finding Description
`isAllowedOrigin` performs wildcard matching like this: [1](#0-0) 

When an allowed origin is configured as `*.ethereum.org`, the code strips the `*.` prefix leaving `allowedHost = "ethereum.org"`, then checks `strings.HasSuffix(originHost, "ethereum.org")`. This check has no boundary requirement (no check that the character before the suffix is a `.`), so any attacker-registered domain that happens to end in the literal string `ethereum.org` — e.g. `evilethereum.org`, `notethereum.org`, `fake-ethereum.org` — will satisfy `HasSuffix` and be treated as a trusted subdomain, even though it is an entirely unrelated, attacker-owned domain.

This matches CWE-346/CWE-453 (CORS misconfiguration due to insecure allowlist logic), analogous to the reported socket.io CVE-2020-28481 issue where an overly permissive default/allowlist check let arbitrary origins bypass same-origin protections. Here the flaw is not a wildcard-by-default, but a broken/bypassable allowlist parser reachable from any unprivileged web client that can control the `Origin` header of a cross-origin request.

Once `isAllowedOrigin` returns true, the handler reflects the caller's `Origin` back verbatim: [2](#0-1) 

This server is the Gateway's `UserServerConfig` HTTP endpoint, which is the internet-facing entry point for external/unprivileged clients submitting JSON-RPC requests to the Gateway (see the sample config enabling `CORSAllowedOrigins = ["https://remix.ethereum.org"]`): [3](#0-2) [4](#0-3) 

### Impact Explanation
If a Gateway operator configures a wildcard allowlist entry (a documented/supported feature — e.g. `*.example.com`), any attacker who registers a domain that merely ends with the same suffix (no subdomain relationship required) can host a malicious webpage there. A browser visiting that page will have its CORS preflight/actual request approved by the Gateway, and the response (which can include JSON-RPC data returned by `ProcessRequest`) will be exposed to the attacker's page via `fetch`/XHR, since `Access-Control-Allow-Origin` is set to the attacker's exact origin. This is a cross-origin allowlist bypass leading to unauthorized read access to otherwise-restricted Gateway responses on behalf of a victim's authenticated/cookie-less session context (impact is bounded by what the endpoint returns to any caller, but it defeats the operator's intended origin restriction).

### Likelihood Explanation
Exploitability requires: (1) the operator opts into a wildcard CORS entry (not the zero-value default, since default `CORSAllowedOrigins = []` and `CORSEnabled = false`), and (2) an attacker registers/controls a domain with the matching suffix. This is a real-world-feasible setup (buying a lookalike domain ending in the same string is trivial) and requires no privileges or prior authentication — purely a browser-based cross-origin request. Likelihood is moderate: it depends on wildcard usage being configured, which the codebase explicitly supports and documents via the `*.` prefix convention and test cases.

### Recommendation
Fix `isAllowedOrigin` to require a dot boundary before the suffix, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org" (keep the dot)
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `evilethereum.org` does not match `*.ethereum.org`, while `foo.ethereum.org` still does.

### Proof of Concept
1. Configure Gateway `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers `https://evilethereum.org` (no subdomain relationship to `ethereum.org`) and serves a page issuing a cross-origin `fetch` to the Gateway's `/user` endpoint with `Origin: https://evilethereum.org`.
3. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and `originHost = "evilethereum.org"`; `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.
4. The Gateway responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker page to read the JSON-RPC response cross-origin — confirmed by the existing (incomplete) test coverage that only exercises non-matching cases like `ethereum.remix.org`/`another.valid.domain.org` but never a same-suffix-no-dot attacker domain: [5](#0-4)

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

**File:** core/scripts/gateway/sample_config.toml (L9-10)
```text
CORSEnabled = false
CORSAllowedOrigins = []
```

**File:** core/services/gateway/integration_tests/gateway_integration_test.go (L59-60)
```go
CORSEnabled = true
CORSAllowedOrigins = ["https://remix.ethereum.org"]
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
