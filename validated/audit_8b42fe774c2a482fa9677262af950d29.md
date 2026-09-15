The code exactly matches the claim, and no existing subdomain-boundary check exists — this is a genuine logic flaw, not a misconfiguration. The wildcard matching feature is a documented, supported pattern (per the code comment and test suite covering wildcard matching), and an attacker can trigger it purely as an unprivileged remote client sending a normal cross-origin `fetch()` with a crafted `Origin` header — no operator/admin access is needed on the attacker's side. The only precondition is that the gateway operator configured a wildcard entry, which is a supported/intended configuration rather than a misuse. The resulting CORS reflection directly matches the in-scope "allowlist bypass" / cross-origin response exposure impact category. This is a real, reachable, code-only bug.

Audit Report

## Title
CORS wildcard-origin allowlist bypass via missing subdomain-boundary check - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in the Gateway's internet-facing HTTP server treats any wildcard entry `*.<suffix>` as matching any `Origin` header whose string simply ends with `<suffix>`, without requiring a `.` boundary. An attacker-owned domain merely ending with the configured suffix (e.g. `evilremix.com` for an allowlist entry `*.remix.com`) passes the check and gets its origin reflected in `Access-Control-Allow-Origin`.

## Finding Description
The wildcard-matching branch strips the `*.` prefix from the configured allowed origin and performs `strings.HasSuffix(originHost, allowedHost)` without verifying that the character preceding the matched suffix is a `.`: [1](#0-0) 
As a result, `originHost` values like `notremix.com` or `evilremix.com` — neither of which is a subdomain of `remix.com` — satisfy the suffix check and are treated as trusted origins. This is confirmed by the actual code in the repository, matching the claim exactly. Scheme and port are still checked correctly before reaching the wildcard branch: [2](#0-1)  but these checks don't prevent the suffix bypass on the host component.

This feeds directly into the CORS response logic: [3](#0-2) 

The existing test suite exercises wildcard matching only for genuine subdomains (`https://remix.ethereum.org` against `https://*.ethereum.org`) and for non-suffix-matching negative cases (`https://ethereum.remix.org` doesn't end with `ethereum.org`), but does not test the boundary-bypass case (e.g., `evilethereum.org` against `*.ethereum.org`), so the flaw is untested and unnoticed: [4](#0-3) 

## Impact Explanation
Any operator using a wildcard `CORSAllowedOrigins` entry (a documented, supported pattern, exercised by `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`) unintentionally allowlists an unbounded set of attacker-registrable domains sharing the trailing suffix. This weakens the origin allowlist enforced by the gateway's public HTTP server, allowing a malicious web page hosted on such a domain to have its cross-origin requests reflected with `Access-Control-Allow-Origin`, undermining the intended trust boundary of the allowlist and enabling cross-origin access to gateway JSON-RPC responses from an attacker-controlled page in a victim's browser.

## Likelihood Explanation
Exploitation requires only that the operator use a wildcard entry (a normal, supported, documented configuration pattern) and that an attacker register/control any domain sharing the suffix string — no privileged access, no DNS rebinding, and no interaction with node internals is needed. The attack is a plain unprivileged cross-origin browser request, fully reproducible and repeatable.

## Recommendation
Fix the wildcard match to require a proper subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```

## Proof of Concept
1. Configure gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]` (mirrors the existing test setup in `core/services/gateway/network/httpserver_test.go`'s `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`).
2. Send a request to the gateway path with header `Origin: https://evilremix.com`.
3. Observe `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilremix.com", "remix.com")` is true, and the response includes `Access-Control-Allow-Origin: https://evilremix.com`, confirmed by tracing `handleRequest` at [3](#0-2) .
4. This can be added as a Go unit test extending `httpserver_test.go`, asserting `Access-Control-Allow-Origin` is empty for origin `https://evilremix.com` against allowlist `https://*.remix.com` — the current implementation would fail this assertion.

### Citations

**File:** core/services/gateway/network/httpserver.go (L172-183)
```go
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
```

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
