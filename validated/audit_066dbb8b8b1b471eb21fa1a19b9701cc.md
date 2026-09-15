The code exactly matches the claim, and this issue doesn't clearly fall under any exclusion in SECURITY.md (it's not theoretical, requires no leaked credentials/privileged access, and CORS wildcard support is a documented/tested feature, not a "misconfiguration"). The impact maps to an in-scope "allowlist bypass" category, and the exploit is triggerable by an unprivileged actor crafting an `Origin` header — no operator/admin access is required beyond the Gateway operator's own supported configuration choice of using a wildcard entry.

Audit Report

## Title
CORS wildcard origin bypass via unanchored suffix match allows lookalike-domain origin spoofing - (File: core/services/gateway/network/httpserver.go)

## Summary
The Gateway's `httpServer.isAllowedOrigin` function validates wildcard `CORSAllowedOrigins` entries (e.g. `*.example.com`) by stripping the `*.` prefix and calling `strings.HasSuffix(originHost, allowedHost)` with no domain-boundary check. This lets an unrelated domain like `evilexample.com` pass as if it were a subdomain of `example.com`, since it merely ends with the same characters.

## Finding Description
In `isAllowedOrigin` [1](#0-0) , once the `*.` prefix is stripped, the remaining comparison `strings.HasSuffix(originHost, allowedHost)` has no requirement that the character preceding the matched suffix be a `.`. Thus `evilexample.com` incorrectly satisfies `strings.HasSuffix("evilexample.com", "example.com")` and is treated as an allowed subdomain of `example.com`, despite being a completely distinct registrable domain. This function is called directly from `handleRequest` [2](#0-1) , which reflects the attacker-supplied `Origin` header into `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true, with no additional validation layer in between. The wildcard-matching feature is a documented, intentional, and tested capability (not a misconfiguration) [3](#0-2) , so the flaw lies purely in the comparison logic itself.

## Impact Explanation
Any Gateway deployment using a wildcard CORS allowlist entry (a supported, tested configuration pattern) is exposed to allowlist bypass: an attacker who controls a domain sharing the same trailing characters as the intended allowed suffix (e.g. `evilexample.com` vs. `*.example.com`) can have their page's cross-origin requests to the Gateway's user/node HTTP endpoint receive a reflected `Access-Control-Allow-Origin` header, letting a browser expose the JSON-RPC response to that unauthorized origin. This is a concrete CORS allowlist-bypass bug in the Gateway's internet-facing HTTP server.

## Likelihood Explanation
Triggering the bug only requires the operator to have enabled `CORSEnabled = true` with a wildcard entry in `CORSAllowedOrigins`, and requires the attacker to control/register a domain with the matching trailing string and to send a request with a spoofed `Origin` header — both are achievable by an unprivileged external actor without any credentials, database, host, or operator access. The bug is deterministic and repeatable for any qualifying origin string.

## Recommendation
Anchor the wildcard match on a domain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    base := allowedHost[2:]
    if originHost == base || strings.HasSuffix(originHost, "."+base) {
        return true
    }
}
```

## Proof of Concept
1. Configure `HTTPServerConfig.CORSEnabled = true` and `CORSAllowedOrigins = []string{"https://*.example.com"}`.
2. Send an HTTP request to the Gateway's user/node endpoint with header `Origin: https://evilexample.com`.
3. Observe `isAllowedOrigin` returns `true` and the response includes `Access-Control-Allow-Origin: https://evilexample.com`, confirmable via a Go unit test mirroring the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` pattern in `core/services/gateway/network/httpserver_test.go`, substituting origin `https://evilexample.com` against allowed origin `https://*.example.com` and asserting the response header is set.

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

**File:** core/services/gateway/network/httpserver_test.go (L152-163)
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
```
