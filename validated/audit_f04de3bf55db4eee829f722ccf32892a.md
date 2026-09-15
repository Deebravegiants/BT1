This confirms the code matches the claim exactly. The `isAllowedOrigin` function at [1](#0-0)  strips the `*.` prefix and then uses `strings.HasSuffix(originHost, allowedHost)` without checking for a domain-separator boundary before the suffix.

Verifying with a concrete example: if `allowedHost` after stripping `*.` is `ethereum.org`, then `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true` in Go, since `"evilethereum.org"` literally ends with the substring `"ethereum.org"` with no dot separator required. This is a real, reachable bug — the function is invoked directly on the `Origin` header of every incoming request at [2](#0-1) , with no other check that enforces a boundary. The existing test suite only checks a negative case with a different TLD structure (`ethereum.remix.org` vs `*.ethereum.org`), which happens to fail the suffix check anyway, but never tests the suffix-collision case (`evilethereum.org`), so the gap is real and untested. This is triggerable by any unauthenticated remote client simply by registering a domain and setting the `Origin` header — no operator/admin access, no host access, and no social engineering required. The impact (CORS allowlist bypass enabling unauthorized cross-origin read of gateway responses) maps to an in-scope Chainlink impact category (gateway request impersonation / allowlist bypass).

The code, exploit path, and impact match all elements of the claim precisely as described.

Audit Report

## Title
CORS wildcard-origin allowlist bypass via missing domain-boundary check - (File: `core/services/gateway/network/httpserver.go`)

## Summary
The gateway HTTP server's `isAllowedOrigin` function matches wildcard CORS allowlist entries (e.g. `https://*.ethereum.org`) using `strings.HasSuffix` on the stripped host string, without requiring a preceding dot separator. This allows any attacker-registered domain that merely shares a string suffix with the allowlisted domain (e.g. `evilethereum.org`) to be treated as an allowed subdomain, bypassing the intended origin restriction.

## Finding Description
In `isAllowedOrigin`, wildcard entries strip the `*.` prefix and compare via `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) . This is a substring/suffix check, not a domain-boundary-aware check — it does not verify that a `.` character (or exact host match) precedes the matched suffix. Consequently, `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates `true`, even though `evilethereum.org` is a completely distinct, attacker-registrable domain unrelated to `ethereum.org`.

This function's result directly controls the `Access-Control-Allow-Origin` response header on every gateway HTTP request: [2](#0-1) . There is no other origin-boundary validation performed before or after this call, so the flawed comparison is the sole gate for wildcard entries.

The existing regression test only exercises a negative case where the origin and allowed pattern are unrelated TLD structures (`ethereum.remix.org` vs `*.ethereum.org`), which naturally fails the suffix check regardless of the boundary bug, so the suffix-collision case is not covered: [3](#0-2) .

## Impact Explanation
An attacker who registers a domain sharing the suffix of an allowlisted wildcard entry (e.g. `evilethereum.org` for `*.ethereum.org`) can have the gateway reflect `Access-Control-Allow-Origin: https://evilethereum.org` in responses, defeating the operator's intended origin allowlist. This permits an attacker-controlled webpage to read cross-origin responses from the gateway in a victim's browser, corresponding to the allowlist bypass / cross-user response corruption impact category recognized for the gateway API.

## Likelihood Explanation
Exploitation only requires (1) the operator configuring a wildcard entry in `CORSAllowedOrigins` (a documented, supported config option), and (2) the attacker registering an inexpensive domain with the right suffix — both fully within reach of an unprivileged, unauthenticated remote actor, with no node/peer compromise, credentials, or host access needed.

## Recommendation
Modify `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` to require a boundary character before the matched suffix, e.g. compare `originHost` against `"." + allowedHost` (keeping the leading dot) instead of the bare stripped host, so `evilethereum.org` no longer matches `*.ethereum.org` while `remix.ethereum.org` still does.

## Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send an HTTP request to the gateway endpoint with header `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, confirming the boundary-unaware `strings.HasSuffix` match in `isAllowedOrigin` incorrectly treats an unrelated domain as an allowed subdomain. This can be added as a unit test in `httpserver_test.go` analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` but asserting the header IS set for `https://evilethereum.org`.

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
