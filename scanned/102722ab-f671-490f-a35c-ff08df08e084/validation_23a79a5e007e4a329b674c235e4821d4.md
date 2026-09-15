### Title
CORS Allowlist Bypass via Improper Suffix Matching in Gateway Wildcard Origin Validation - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway HTTP server's CORS origin validation (`isAllowedOrigin`) implements wildcard subdomain matching using a naive `strings.HasSuffix` check without verifying a required domain-label boundary (a preceding `.`). This allows an attacker to register a domain that merely *ends with* the allowed suffix (e.g. `evilethereum.org` for an allowlist entry `*.ethereum.org`) and have the Gateway falsely treat it as a legitimate subdomain, echoing that attacker origin back in `Access-Control-Allow-Origin` and enabling credentialed cross-origin reads of Gateway responses — the same bug class as CVE-2021-38019 (insufficient CORS policy enforcement leaking cross-origin data).

### Finding Description
In `isAllowedOrigin`, the wildcard branch strips the `*.` prefix from the configured allowed origin and then checks: [1](#0-0) 

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

`strings.HasSuffix(originHost, allowedHost)` only checks that `originHost` ends with the literal characters of `allowedHost` — it does **not** require a `.` (label separator) immediately before the match. As a result, an origin host like `evilethereum.org` will match an allowlist entry `*.ethereum.org` (`allowedHost` = `"ethereum.org"`), because `"evilethereum.org"` ends with the substring `"ethereum.org"`, even though `evilethereum.org` is a completely unrelated, attacker-registrable domain and not a subdomain of `ethereum.org`.

This function is invoked directly from the internet-facing request handler in `handleRequest`, which echoes the raw `Origin` header back as `Access-Control-Allow-Origin` whenever `isAllowedOrigin` returns true: [2](#0-1) 

The existing test suite even documents the intended (safe) wildcard behavior — e.g. rejecting `https://ethereum.remix.org` as not ending with `ethereum.org` — but does not cover the boundary-less suffix bypass case (attacker domain literally ending in the allowed suffix without a dot separator): [3](#0-2) 

### Impact Explanation
The Gateway is an internet-facing component that accepts unauthenticated/JWT-bearing requests from external initiators and DON clients. A successful bypass lets an attacker's malicious webpage (hosted at a spoofable domain such as `evilethereum.org` or `notgateway.example.com`-style constructions crafted to end with the trusted suffix) receive `Access-Control-Allow-Origin` set to its own origin along with `Access-Control-Allow-Credentials`-style browser behavior enabled by the CORS handshake, permitting a victim's browser to make credentialed cross-origin requests to the Gateway and have the attacker page read the response (session/JWT-authenticated Gateway responses, job-run data, or other sensitive payloads routed through the gateway handler). This maps to unauthorized cross-user response confusion / allowlist bypass reachable from an unprivileged remote client.

### Likelihood Explanation
Exploitation only requires registering an unremarkable-looking domain name whose registrable/base portion literally ends with the operator's configured wildcard suffix (e.g., register `evil<allowed-suffix>` or a domain crafted so its full host string ends with the allowed suffix) and hosting a CORS-triggering webpage there — no privileged access, no node compromise, and no network-layer trust required. Any Gateway operator using `CORSAllowedOrigins` wildcard entries (`*.domain.tld`) is affected.

### Recommendation
Fix the suffix check to enforce a proper label boundary, e.g.:
```go
if strings.HasSuffix(originHost, allowedHost) &&
    (originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)) {
    return true
}
```
This ensures `originHost` is either exactly `allowedHost` or a true subdomain of it (preceded by a `.`), preventing suffix-only spoofing like `evilethereum.org` matching `*.ethereum.org`.

### Proof of Concept
1. Configure Gateway with `CORSAllowedOrigins = ["*.ethereum.org"]` and `CORSEnabled = true`.
2. From a browser, host a page at `https://evilethereum.org` (attacker-registered domain).
3. Send a fetch/XHR request with `Origin: https://evilethereum.org` to the Gateway endpoint.
4. `isAllowedOrigin("https://evilethereum.org")` splits `allowedHost` to `"ethereum.org"` and checks `strings.HasSuffix("evilethereum.org", "ethereum.org")`, which evaluates `true`.
5. The Gateway responds with `Access-Control-Allow-Origin: https://evilethereum.org`, and the attacker page's browser-based JavaScript can read the cross-origin Gateway response, despite `evilethereum.org` never being an intended trusted subdomain of `ethereum.org`.

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
