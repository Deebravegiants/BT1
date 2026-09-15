The code confirms the claim exactly as described. The vulnerability is real and accurately documented.

Audit Report

## Title
CORS wildcard-origin allowlist bypass via unanchored suffix match in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in [1](#0-0)  strips the `*.` prefix from a configured wildcard allowed origin and performs a raw `strings.HasSuffix(originHost, allowedHost)` check with no requirement that a `.` boundary precede the matched suffix. This allows any attacker-controlled hostname that merely ends with the configured domain's characters (e.g. `evilethereum.org` matching a `*.ethereum.org` rule) to be treated as an allowed origin, even though it is not a genuine subdomain.

## Finding Description
The wildcard-matching branch is:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [1](#0-0) 

Given an allowlist entry `https://*.ethereum.org`, `allowedHost` becomes `ethereum.org` after stripping the wildcard prefix. `strings.HasSuffix` only checks that `originHost` ends with the literal bytes `ethereum.org`, with no dot-boundary check. Consequently, hosts like `evilethereum.org`, `notethereum.org`, or `attacker-ethereum.org` incorrectly satisfy the suffix condition despite not being true subdomains of `ethereum.org`.

This function feeds directly into `handleRequest`, which reflects the raw, attacker-supplied `Origin` header value into `Access-Control-Allow-Origin` whenever `isAllowedOrigin` returns true, with no further validation:
```go
if s.isAllowedOrigin(origin) {
    w.Header().Set("Access-Control-Allow-Origin", origin)
    ...
``` [2](#0-1) 

There is no dedicated CORS library in use here — this is a hand-rolled origin matcher, and no other middleware or check compensates for the missing subdomain boundary check. This is the exact bug class described in GHSA-869c-j7wc-8jqv (Gin CORS wildcard mishandling).

## Impact Explanation
An unauthenticated, unprivileged attacker who registers a domain ending in the same substring as an operator-configured wildcard suffix (e.g., `evilethereum.org` vs. `*.ethereum.org`) can have their origin reflected into `Access-Control-Allow-Origin`. This lets a victim's browser expose cross-origin Gateway API responses to the attacker's page — a genuine CORS/allowlist bypass (CWE-346) that falls under the "allowlist or subscription bypass" / "cross-user response corruption" categories relevant to Chainlink's Gateway bounty scope. The severity depends on what data/actions the Gateway API exposes to browser-originated requests, but the bypass itself is concrete and directly caused by this code path, not by any external or operator misconfiguration beyond the documented, supported wildcard feature.

## Likelihood Explanation
Exploitability requires the operator to enable `CORSEnabled: true` and configure at least one wildcard entry in `CORSAllowedOrigins` (e.g. `https://*.ethereum.org`). This is an explicitly supported, tested configuration pattern, confirmed by `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` [3](#0-2) , not a misconfiguration or unsupported edge case. Once wildcard CORS is enabled, exploitation requires only registering a domain with the right suffix and getting a victim's browser to visit an attacker page — no credentials, roles, or node/DON compromise needed. This is a fully unprivileged, client-triggerable bug in default supported configuration.

## Recommendation
Enforce a subdomain boundary when matching wildcard hosts:
```go
if strings.HasPrefix(allowedHost, "*.") {
    base := allowedHost[2:]
    if originHost == base || strings.HasSuffix(originHost, "."+base) {
        return true
    }
}
```
Add regression tests for suffix-but-not-subdomain hostnames (e.g., `evilethereum.org`, `notethereum.org`) against a `*.ethereum.org` rule to ensure they are rejected while genuine subdomains (e.g., `foo.ethereum.org`) still pass.

## Proof of Concept
1. Configure Gateway with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.ethereum.org"}`.
2. Send an HTTP POST to the Gateway with header `Origin: https://evilethereum.org`.
3. Observe `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`.
4. Observe the response contains `Access-Control-Allow-Origin: https://evilethereum.org`.
5. Add a Go unit test analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` [3](#0-2)  asserting that origin `https://evilethereum.org` against allowlist `https://*.ethereum.org` should NOT receive `Access-Control-Allow-Origin`, which fails against current code.

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

**File:** core/services/gateway/network/httpserver.go (L196-202)
```go
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
