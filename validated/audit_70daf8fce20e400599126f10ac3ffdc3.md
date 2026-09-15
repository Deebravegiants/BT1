Based on my review of the code, the claim is confirmed. The existing test suite even documents the flawed behavior without catching this edge case — `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` tests `https://ethereum.remix.org` against `*.ethereum.org` (which correctly fails since it doesn't end with `ethereum.org`), but there is no test for a suffix-sharing attacker domain like `evilethereum.org` or `notethereum.org`, which would incorrectly pass `strings.HasSuffix(originHost, allowedHost)` at [1](#0-0) . This confirms the root cause is real and untested.

Audit Report

## Title
CORS wildcard origin matching in gateway HTTP server accepts non-subdomain hosts sharing a suffix - (File: core/services/gateway/network/httpserver.go)

## Summary
`httpServer.isAllowedOrigin` implements wildcard CORS origin matching by stripping the `*.` prefix from a configured allowlist entry and testing whether the attacker-supplied `Origin` header host has that stripped string as a raw suffix via `strings.HasSuffix`, without requiring a `.` boundary before the match. This lets an attacker-registered domain like `evilexample.com` satisfy a `*.example.com` allowlist entry.

## Finding Description
In `isAllowedOrigin`, for a configured entry such as `*.example.com`, the code strips the `*.` prefix to get `example.com`, then checks `strings.HasSuffix(originHost, allowedHost)` [2](#0-1) . This is a purely lexical suffix check with no requirement that the character preceding the match in `originHost` be a `.`. An `Origin` such as `https://evilexample.com` satisfies `strings.HasSuffix("evilexample.com", "example.com")` and is incorrectly treated as trusted. The `Origin` header is fully attacker-controlled and processed unauthenticated in `handleRequest` [3](#0-2) , which is reachable by any unprivileged client hitting the Gateway's public HTTP endpoint. The existing scheme/port equality checks and exact-host check do not mitigate this, since the flaw is specifically in the wildcard suffix branch [4](#0-3) . The existing test suite covers negative cases where the origin doesn't end with the suffix at all (e.g. `ethereum.remix.org` vs `*.ethereum.org`) but has no test for a suffix-sharing non-subdomain attacker domain, confirming this gap was not caught [5](#0-4) .

## Impact Explanation
If `isAllowedOrigin` returns true for an origin that was never intended to be trusted, `handleRequest` sets `Access-Control-Allow-Origin` to that attacker's origin [6](#0-5) , allowing a page hosted on an attacker-registered domain to make cross-origin browser requests to the Gateway and read JSON-RPC responses via `fetch`/`XHR`. This is a concrete cross-origin allowlist bypass, mapping to the "allowlist bypass / cross-user response corruption" impact class, since responses intended only for `*.example.com` become readable by an unrelated attacker-controlled origin.

## Likelihood Explanation
Exploitation requires the Gateway operator to have enabled `CORSEnabled = true` with at least one wildcard entry in `CORSAllowedOrigins`, which is a documented supported configuration pattern (per `core/scripts/gateway/sample_config.toml`). Given that precondition (which is normal, intended feature usage rather than a misconfiguration), no authentication or privilege is required by the attacker — only registering a domain lexically ending with the allowlisted suffix and getting a victim's browser to send a request to the Gateway while visiting the attacker's page. This is reproducible deterministically and repeatably.

## Recommendation
Enforce a label boundary in the wildcard branch: after stripping `*.`, require either `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)`, so `evilexample.com` cannot match `*.example.com` while `sub.example.com` still can.

## Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Extend `core/services/gateway/network/httpserver_test.go`'s `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`-style test with origin `https://evilexample.com` (no relation to `example.com`).
3. Assert `resp.Header.Get("Access-Control-Allow-Origin")` equals `https://evilexample.com`, demonstrating `strings.HasSuffix("evilexample.com", "example.com")` incorrectly returns `true` at [7](#0-6) .

### Citations

**File:** core/services/gateway/network/httpserver.go (L172-190)
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
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
		}
```

**File:** core/services/gateway/network/httpserver.go (L195-203)
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
