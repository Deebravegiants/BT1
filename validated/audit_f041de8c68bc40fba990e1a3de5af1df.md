### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - ([File: core/services/gateway/network/httpserver.go])

### Summary
The gateway's internet-facing HTTP server validates the `Origin` header against a configured wildcard allowlist (e.g. `https://*.ethereum.org`) using an unanchored `strings.HasSuffix` check. Because the match is not anchored on a domain-label boundary (no check for a preceding `.`), any attacker-controlled domain that merely *ends with* the configured suffix — not just a genuine subdomain — is treated as an allowed origin. This mirrors the root cause of CVE-2024-1132 (Keycloak's improper wildcard validation in redirect URIs): a "wildcard" match implemented as a raw substring/suffix test rather than a structurally-anchored match, letting unprivileged clients bypass an allowlist.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  checks for wildcard host matches like this:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

Given `CORSAllowedOrigins = ["https://*.ethereum.org"]`, `allowedHost` becomes `"ethereum.org"`. The code then accepts any `originHost` for which `strings.HasSuffix(originHost, "ethereum.org")` is true. This is true not only for legitimate subdomains such as `remix.ethereum.org`, but also for any attacker-registered domain that happens to end with the literal string `ethereum.org`, e.g. `evilethereum.org`, `attacker-ethereum.org`, or `notethereum.org`. There is no check that the character preceding the suffix in `originHost` is a `.` (or that the suffix begins at a label boundary), so the wildcard match is not actually scoped to subdomains of the allowed domain.

This check feeds directly into the CORS response in `handleRequest`, at [2](#0-1) :
```go
if s.config.CORSEnabled {
    origin := r.Header.Get("Origin")
    if s.isAllowedOrigin(origin) {
        w.Header().Set("Access-Control-Allow-Origin", origin)
        ...
```
The `Origin` header is fully attacker-controlled (any unprivileged web client), and reflecting it with `Access-Control-Allow-Origin` when `isAllowedOrigin` wrongly returns `true` allows a malicious website to make authenticated/credentialed cross-origin requests to the gateway and read the JSON-RPC responses in the browser.

The existing test suite only exercises genuine subdomains and non-matching-suffix cases (e.g. `https://ethereum.remix.org` correctly rejected because it doesn't *end* with `ethereum.org`), per [3](#0-2) , but it never tests a domain like `evilethereum.org` that satisfies `HasSuffix` while not being a real subdomain, so the flaw is not caught by tests.

### Impact Explanation
This gateway HTTP server is internet-facing and used to relay JSON-RPC requests/responses (e.g., vault secret operations processed through `GatewayVaultRequestProcessor`, per [4](#0-3) ). If an operator configures a wildcard CORS allowlist entry (a documented and intended usage pattern, confirmed by the `*.ethereum.org` test cases), an attacker who registers a similarly-suffixed domain can have their site treated as a trusted origin. This enables cross-origin reading of gateway responses that a legitimate origin would otherwise receive, potentially exposing sensitive JSON-RPC response data to an unauthorized site — a cross-user/cross-origin response confusion analogous to the redirect-based information disclosure in the Keycloak advisory.

### Likelihood Explanation
Exploitation only requires: (1) the gateway operator has configured at least one wildcard entry in `CORSAllowedOrigins` (an explicitly supported and tested configuration), and (2) the attacker registers/controls any domain name ending in the same suffix and lures a victim into visiting it with a browser while the browser sends credentialed requests to the gateway. No privileged access or node compromise is required — the bug is directly reachable from an unprivileged client via a crafted `Origin` header.

### Recommendation
Fix `isAllowedOrigin` in [5](#0-4)  to anchor the wildcard match on a domain-label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` must either equal the base domain or end with `.` + the base domain, rejecting lookalike domains like `evilethereum.org`. Add regression tests covering suffix-only (non-subdomain) lookalike origins.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser on `https://evilethereum.org`, send a cross-origin `fetch` request to the gateway's JSON-RPC endpoint with credentials included.
3. The server's `isAllowedOrigin("https://evilethereum.org")` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`, so the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, letting the attacker page read the response body in violation of the intended origin restriction.

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-193)
```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	originScheme, originHost, originPort, err := s.splitURL(origin)
	if err != nil {
		s.lggr.Debug("error parsing origin URL", err)
		return false
	}
	for _, allowed := range s.config.CORSAllowedOrigins {
		// probably better to do this once when server starts and store it in a map
		// this is an easier solution so we don't have to apply more changes to the code
		// just need to be careful when specifying allowed origins in the config file
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
		if err != nil {
			s.lggr.Debug("error parsing allowed origin URL", err)
			continue
		}
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
	}
	return false
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L20-40)
```go
// GatewayVaultRequestProcessor orchestrates the shared gateway-routed vault JSON-RPC pipeline
// used by the gateway public handler and the node-side gateway connector handler.
//
// Pipeline invariant:
//
//	ValidateStructureBeforeAuth → AuthorizeRequest → Prefix ID → StampAuthorizedParams → ValidateOwnerScopedLimits
//	    (no param mutation)        (on raw bytes)               (namespace + request_id)      (ciphertext size)
//
// AuthorizeRequest runs while params are still digest-safe. It also applies the replay guard
// (digest deduplication) and validates that payload owners match the authorized workflow owner
// before this processor rewrites the request ID or stamps params.
//
// Owner-scoped limit checks are deferred until after authorization: each new owner tenant
// registered by a scoped limiter spawns a persistent background updater, so checking them
// pre-auth would let unauthenticated callers create unbounded limiter tenants.
type GatewayVaultRequestProcessor struct {
	validator               *RequestValidator
	authorizer              Authorizer
	stripOwnerPrefixForAuth bool
	lggr                    logger.Logger
}
```
