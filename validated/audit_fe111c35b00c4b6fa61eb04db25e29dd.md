Audit Report

## Title
Sibling-Domain CORS Origin Bypass via Boundary-less Suffix Match - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` validates wildcard CORS entries (e.g. `*.remix.com`) using `strings.HasSuffix(originHost, allowedHost)` without requiring a domain-label boundary (`.`) before the matched suffix. As a result, an attacker-controlled origin such as `evilremix.com` or `notremix.com` incorrectly satisfies the suffix check intended to allow only genuine subdomains of `remix.com`.

## Finding Description
The confirmed code at [1](#0-0)  shows that after stripping the `*.` prefix from the allowed host, the check is a raw `strings.HasSuffix(originHost, allowedHost)` with no verification that the character preceding the matched suffix in `originHost` is a `.`. The scheme and port checks that precede it are exact-match and not vulnerable [2](#0-1) . This is a genuine boundary-less suffix comparison bug: `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`, so a completely different registrable domain that merely ends with the same character sequence is treated as an authorized subdomain.

The result of `isAllowedOrigin` directly controls whether the `Origin` header is reflected into `Access-Control-Allow-Origin` in `handleRequest` [3](#0-2) , before the raw request body is read and forwarded to `s.handler.ProcessRequest` along with any extracted JWT [4](#0-3) . No other validation layer re-checks the origin boundary, so the flaw is not mitigated elsewhere in the request path.

## Impact Explanation
This allows a browser-based attacker whose page is hosted on an unrelated domain that happens to share a trailing substring with the operator's configured wildcard allowlist (e.g. `evilremix.com` vs `*.remix.com`) to have its `Origin` reflected back with permissive CORS headers. This enables the attacker's page to read Gateway JSON responses via `fetch`/`XHR` for any victim whose browser is induced to issue a request to the Gateway with credentials/session context, i.e., cross-user response exposure via CORS impersonation of an intended-but-unrelated origin. This maps to the in-scope "cross-user response corruption" / gateway request impersonation impact category.

## Likelihood Explanation
The precondition is that the operator enables CORS with at least one wildcard entry (`CORSAllowedOrigins = ["https://*.remix.com"]`), a documented, supported configuration pattern (present in `core/scripts/gateway/sample_config.toml`). Given that, any unprivileged external actor can register a domain sharing the vulnerable suffix and use a normal browser to trigger the bypass — no credentials, admin access, or victim-side code changes are required beyond standard cross-origin browser behavior. The exploit is deterministic and repeatable.

## Recommendation
Enforce a domain-label boundary in the wildcard match, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
This ensures only true subdomains of the allowed host (values immediately preceded by a `.`) are matched, eliminating sibling/lookalike domain bypass.

## Proof of Concept
1. Start the Gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. Send `GET /health` or the configured request path with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`.
4. Alternatively, add a Go unit test to `core/services/gateway/network/httpserver_test.go` calling `isAllowedOrigin("https://evilremix.com")` with config `CORSAllowedOrigins: []string{"https://*.remix.com"}` and assert it returns `true` (demonstrating the bypass), contrasted with the expected `false`.

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

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```
