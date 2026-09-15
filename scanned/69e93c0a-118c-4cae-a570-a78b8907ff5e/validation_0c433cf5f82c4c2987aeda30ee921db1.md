The `httpserver.go` CORS origin-matching logic contains the exact same bug class as the reported `safeurl-python` SSRF: an allowlist match based on `strings.HasSuffix` without verifying a domain-boundary (dot) before the suffix.### Title
CORS allowlist bypass via improper wildcard-suffix domain matching in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's `httpServer.isAllowedOrigin` implements a wildcard CORS allowlist (e.g. `*.remix.com`) by stripping the `*.` prefix and then testing the request's `Origin` header host with `strings.HasSuffix(originHost, allowedHost)`. This is the same root-cause bug class as CVE-2023-24622 (safeurl-python): a suffix/prefix string match used for domain allowlisting without enforcing a `.`-boundary before the matched suffix, so an attacker-registered domain that merely *ends with* the allowed suffix (with no dot separator) is incorrectly treated as a subdomain of the trusted origin.

### Finding Description
`isAllowedOrigin` parses both the incoming `Origin` header and each configured allowed origin with `splitURL`, then for wildcard entries does: [1](#0-0) 

Given an allowed origin `https://*.ethereum.org`, `allowedHost` becomes `ethereum.org`. The check `strings.HasSuffix(originHost, allowedHost)` will match not only legitimate subdomains like `remix.ethereum.org`, but also any attacker-registered domain such as `evilethereum.org`, `notethereum.org`, or `attacker-ethereum.org` — none of which are subdomains of `ethereum.org`, since there is no dot separator enforced before the suffix. This mirrors the exact defect described in the safeurl-python advisory, where `re.match("(?i)^%s" % domain, value)` allowed `victimacomattacker.com` to pass an allowlist for `victim.com` because the check anchored only one end of the string and ignored the domain-boundary character.

This check is invoked from the request handling path reachable by any unprivileged client sending an HTTP request with an `Origin` header: [2](#0-1) 

### Impact Explanation
When `CORSEnabled` is true and an operator configures a wildcard allowlist entry (e.g. `*.ethereum.org` as shown in existing tests), an attacker who registers or controls a domain that merely ends with the same suffix without a dot boundary (e.g. `evilethereum.org`) can have their `Origin` reflected back in `Access-Control-Allow-Origin`, along with `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`. This lets a page hosted on the attacker's look-alike domain make cross-origin `fetch`/XHR calls to the Gateway's JSON-RPC endpoint and have the browser permit reading the response, bypassing the intended Same-Origin restriction the allowlist was meant to enforce. Since the endpoint also accepts a bearer `Authorization` token supplied by the calling frontend code, any web app or tooling that stores/passes such tokens client-side and unintentionally exposes them to script running on the attacker's confusable domain could have its Gateway responses read cross-origin.

### Likelihood Explanation
Exploitation only requires (1) the operator to enable `CORSEnabled` with a wildcard allowlist entry — a documented, supported configuration exercised directly in the codebase's own tests — and (2) the attacker registering an inexpensive look-alike domain (e.g. `evil<suffix>` with no dot), which is trivial and cheap. No privileged access, no node compromise, and no network-layer position is required — a public unprivileged client simply sets the `Origin` header, which any browser or HTTP client does automatically for cross-origin requests.

### Recommendation
Change the wildcard suffix check to require a subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This ensures `evilethereum.org` is rejected while `remix.ethereum.org` and `ethereum.org` itself remain correctly matched.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`, analogous to the existing test setup: [3](#0-2) 
2. From a page hosted at `https://evilethereum.org` (attacker-controlled, no relation to `ethereum.org`), send a `fetch` request to the Gateway endpoint with `Origin: https://evilethereum.org`.
3. Because `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates to `true`, `isAllowedOrigin` returns `true` and the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, permitting the attacker's page to read the JSON-RPC response cross-origin — despite `evilethereum.org` not being an actual subdomain of `ethereum.org`.

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

**File:** core/services/gateway/network/httpserver_test.go (L152-166)
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
