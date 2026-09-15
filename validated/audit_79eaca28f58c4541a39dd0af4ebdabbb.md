The code confirms the claim exactly as described. The vulnerable logic is real and unmodified from what's cited.Audit Report

## Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - ([File: core/services/gateway/network/httpserver.go])

## Summary
`isAllowedOrigin` in [1](#0-0)  uses `strings.HasSuffix(originHost, allowedHost)` to implement wildcard CORS matching (e.g. `*.ethereum.org`) without requiring a `.` boundary before the matched suffix. An attacker who registers/hosts a domain that merely ends with the allowed suffix as a raw string (e.g. `evilethereum.org` vs. allowed `ethereum.org`) is treated as a subdomain and gets whitelisted, causing the gateway to reflect the attacker's `Origin` into `Access-Control-Allow-Origin`.

## Finding Description
The wildcard branch strips the `*.` prefix and does a raw suffix check with no requirement that the preceding character be `.`, so `originHost = "evilethereum.org"` incorrectly satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org")`, even though `evilethereum.org` is an unrelated, independently registrable domain rather than a subdomain of `ethereum.org`. This function is called directly from `handleRequest` for every request the internet-facing gateway HTTP server processes: [2](#0-1)  — if `isAllowedOrigin` returns true, the raw attacker-supplied `Origin` header is reflected verbatim into `Access-Control-Allow-Origin`, with no further validation. The existing regression test only checks a case where the suffix genuinely doesn't match (`ethereum.remix.org` vs `ethereum.org`), not the boundary-less concatenation case, so this bypass is untested: [3](#0-2) .

## Impact Explanation
This is an allowlist bypass on the gateway's browser-facing CORS enforcement. When an operator configures `CORSAllowedOrigins` with a wildcard entry (a documented, supported feature present in sample configs and referenced elsewhere in the codebase), any attacker-controlled site whose hostname happens to end with the same substring — not a true subdomain — gets its origin reflected into `Access-Control-Allow-Origin`. This lets an unrelated, attacker-controlled website read cross-origin JSON-RPC-style responses from the gateway in a victim's browser session, breaking the intended origin isolation of the gateway HTTP API. This maps to the in-scope "gateway request impersonation / cross-user response corruption" impact category, since a browser is tricked into disclosing response data to a site it shouldn't trust.

## Likelihood Explanation
No privileged access, credential, or host access is needed by the attacker — only registering/hosting a domain with the right suffix and getting a victim's browser to issue a cross-origin request with that origin. The only "operator" involvement is configuring a wildcard allowlist entry, which is a normal, supported configuration (not a misconfiguration outside intended use), so the vulnerability is triggerable in a realistic deployment. The bug is deterministic and reproducible by construction of `strings.HasSuffix`.

## Recommendation
Anchor the wildcard match to a genuine label boundary:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` must equal the bare domain or end with `.` + domain, never merely with a raw substring match. Add a regression test asserting `https://evilethereum.org` is rejected against `https://*.ethereum.org`.

## Proof of Concept
1. Start `httpServer` with `CORSEnabled: true`, `CORSAllowedOrigins: []string{"https://*.ethereum.org"}` (as done in `startNewServer` in `httpserver_test.go`).
2. Send a request with header `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, confirming `isAllowedOrigin` incorrectly returns `true` via the unanchored `strings.HasSuffix` check.
4. Add this as a table case alongside the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` test in [3](#0-2)  to demonstrate the current test suite does not catch this bypass.

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
