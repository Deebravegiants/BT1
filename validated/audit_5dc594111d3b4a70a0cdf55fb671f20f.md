Only a single "Initial commit" exists, so this is not a previously fixed/disclosed issue in this repo's history. The code matches the claim exactly, and the vulnerability is genuine.

Audit Report

## Title
CORS wildcard allowlist bypass via missing domain-label boundary check - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway's `isAllowedOrigin` function validates wildcard CORS allowlist entries (e.g. `*.remix.com`) using a plain `strings.HasSuffix` check against the origin host, without verifying that the matched suffix begins at a domain-label boundary. As a result, any attacker-registered domain that merely ends with the allowed suffix string (e.g. `evilremix.com`) — not an actual subdomain — is treated as an allowed CORS origin.

## Finding Description
In `isAllowedOrigin` [1](#0-0) , when an allowlist entry has the `*.` prefix, the code strips the prefix and then checks `strings.HasSuffix(originHost, allowedHost)`. This check only verifies that `originHost` ends with the literal string `allowedHost`; it does not require a `.` separator (or equality) immediately preceding the match. Consequently, for an allowlist entry `*.remix.com`, an origin host `evilremix.com` satisfies `strings.HasSuffix("evilremix.com", "remix.com") == true`, despite `evilremix.com` not being a subdomain of `remix.com` at all.

This function is called directly from `handleRequest` [2](#0-1) , which is registered as the handler for the gateway's public request path via `mux.Handle(config.Path, handler)` [3](#0-2) . When `isAllowedOrigin` returns `true`, the server reflects the caller-supplied `Origin` header verbatim into `Access-Control-Allow-Origin`, along with permissive `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`. No other check (scheme/port matching aside) constrains the wildcard suffix match to a proper subdomain relationship.

## Impact Explanation
This is an in-scope allowlist bypass at the gateway's CORS trust boundary. An attacker who registers a domain whose name happens to end with a configured allowed suffix (trivial and requires no special access — e.g., `evilremix.com`, `notremix.com`) can have their origin reflected into `Access-Control-Allow-Origin`, allowing browser JavaScript hosted on that attacker-controlled domain to make cross-origin requests to the gateway and read the JSON-RPC responses (which can include job run results, vault/secrets-related metadata, or other response data) as if it were a legitimate subdomain of the trusted domain. This maps to the "allowlist or subscription bypass" / "gateway request impersonation" impact category.

## Likelihood Explanation
Exploitation requires only registering an inexpensive look-alike domain name and hosting a page that issues a request to the gateway endpoint from a victim's browser — no credentials, node/operator access, or privileged role are needed. The bug is reachable whenever the gateway operator configures any wildcard entry in `CORSAllowedOrigins`, which is an explicitly supported configuration pattern (confirmed by the existing wildcard test `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`) [4](#0-3) , making this a realistic, repeatable misconfiguration-adjacent bug rather than a hypothetical one.

## Recommendation
Require a domain-label boundary when matching the wildcard suffix:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```

## Proof of Concept
1. Configure the gateway with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.remix.com"}`.
2. Send an HTTP request to the gateway's configured `config.Path` with header `Origin: https://evilremix.com`.
3. Observe that `isAllowedOrigin` returns `true` via `strings.HasSuffix("evilremix.com", "remix.com")`, and the response contains `Access-Control-Allow-Origin: https://evilremix.com`, confirming an unrelated domain is granted CORS trust intended only for `remix.com` and its true subdomains. This can be verified with a Go unit test analogous to `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards` but asserting rejection of `https://evilremix.com` against allowlist `https://*.remix.com`, which currently fails (is incorrectly allowed).

### Citations

**File:** core/services/gateway/network/httpserver.go (L107-114)
```go
	mux := http.NewServeMux()
	var handler http.Handler
	handler = http.HandlerFunc(server.handleRequest)
	if config.RequestTimeoutMillis > 0 {
		handler = http.TimeoutHandler(handler, time.Duration(config.RequestTimeoutMillis)*time.Millisecond, "Request timed out")
	}
	mux.Handle(config.Path, handler)
	mux.Handle(HealthCheckPath, http.HandlerFunc(server.handleHealthCheck))
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

**File:** core/services/gateway/network/httpserver_test.go (L152-157)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://*.gov"})

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)
```
