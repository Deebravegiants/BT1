This confirms the claim accurately reflects the code. The `isAllowedOrigin` function at line 187 performs `strings.HasSuffix(originHost, allowedHost)` without checking for a `.` boundary before the suffix, so `evilethereum.org` would indeed satisfy `HasSuffix("evilethereum.org", "ethereum.org")` and be incorrectly treated as a subdomain match for a `*.ethereum.org` wildcard entry.

This is a real logic bug: the wildcard suffix comparison at [1](#0-0)  lacks a DNS label-boundary check, allowing any origin string that merely ends with the configured suffix (not just true subdomains) to pass. The vulnerable function is reached directly from `handleRequest` for every request to the gateway's user-facing server [2](#0-1) , and when it returns true, `Access-Control-Allow-Origin` is set to the attacker-controlled origin verbatim, enabling a browser to read cross-origin JSON-RPC responses. This requires the operator to enable `CORSEnabled` with a `*.`-prefixed wildcard entry — a documented, supported configuration exercised in the existing test suite [3](#0-2) , but exploitation itself requires no special privilege from the attacker beyond registering a domain and sending a crafted `Origin` header, which is normal unprivileged client behavior. This maps to the in-scope "cross-user response corruption" / CORS allowlist bypass impact category since it allows an unintended origin to receive the gateway's response data via the browser fetch API.

Audit Report

## Title
CORS wildcard-origin allowlist bypass via missing label-boundary check enables origin spoofing - ([File: core/services/gateway/network/httpserver.go])

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` validates wildcard CORS entries (e.g. `*.ethereum.org`) using a bare `strings.HasSuffix(originHost, allowedHost)` check without requiring a `.` label boundary. This lets an attacker-controlled domain that merely ends with the configured suffix string (e.g. `evilethereum.org`) be treated as an allowed subdomain, causing the gateway to echo `Access-Control-Allow-Origin` for that spoofed origin.

## Finding Description
In `isAllowedOrigin`, after stripping the `*.` prefix from a configured wildcard entry, the code checks `strings.HasSuffix(originHost, allowedHost)` at [1](#0-0) . `HasSuffix` performs a raw string suffix comparison, not a DNS-label-aware comparison, so `originHost = "evilethereum.org"` satisfies `HasSuffix("evilethereum.org", "ethereum.org")` even though it is an unrelated registrable domain, not a subdomain of `ethereum.org`. This function is invoked directly in `handleRequest` for every request to the gateway's user-facing HTTP server, and on a true result the server unconditionally sets `Access-Control-Allow-Origin` to the raw, attacker-supplied `Origin` header value [2](#0-1) . No other check (exact match, scheme/port match) compensates for this, since the exact-match and scheme/port checks pass through unaffected and only the wildcard suffix branch is flawed [4](#0-3) .

## Impact Explanation
Any unprivileged web page hosted on a domain crafted to end with the operator's configured allowed suffix (e.g. registering `evilethereum.org` to bypass an `*.ethereum.org` allowlist entry) can pass the CORS check and receive `Access-Control-Allow-Origin` reflecting its own spoofed origin. This allows a browser-based cross-origin script to read the gateway's `/user` JSON-RPC responses via `fetch`, constituting a CORS allowlist bypass / cross-user response exposure — an in-scope Chainlink gateway impact class.

## Likelihood Explanation
Exploitation requires the operator to enable `CORSEnabled = true` with at least one `*.`-prefixed wildcard entry in `CORSAllowedOrigins`, a supported and exercised configuration pattern per the existing test suite (`TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`) [3](#0-2) . Given that precondition, the attacker needs only to register/control a domain ending in the same substring and send a normal cross-origin request with a crafted `Origin` header — no elevated privileges, credentials, or victim interaction beyond visiting the attacker's page are required.

## Recommendation
Enforce a proper DNS label boundary in the wildcard match, e.g. require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix(originHost, allowedHost)`, so that `evilethereum.org` no longer matches an `ethereum.org` wildcard allowlist entry.

## Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From an attacker-controlled page served at `https://evilethereum.org`, send a request to the gateway's `/user` endpoint with header `Origin: https://evilethereum.org`.
3. `splitURL` parses `originHost = "evilethereum.org"`; the wildcard entry strips to `allowedHost = "ethereum.org"`; `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, which can be verified by extending `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` in `core/services/gateway/network/httpserver_test.go` with `origin := "https://evilethereum.org"` and asserting the response header is incorrectly set to that value [5](#0-4) .

### Citations

**File:** core/services/gateway/network/httpserver.go (L163-167)
```go
	for _, allowed := range s.config.CORSAllowedOrigins {
		// probably better to do this once when server starts and store it in a map
		// this is an easier solution so we don't have to apply more changes to the code
		// just need to be careful when specifying allowed origins in the config file
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
```

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

**File:** core/services/gateway/network/httpserver_test.go (L152-165)
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
