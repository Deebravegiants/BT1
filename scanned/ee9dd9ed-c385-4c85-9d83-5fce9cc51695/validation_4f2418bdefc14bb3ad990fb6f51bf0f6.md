### Title
CORS Wildcard Origin Bypass via Unanchored Suffix Match in Gateway HTTP Server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's `httpServer.isAllowedOrigin` function implements wildcard CORS origin matching using an unanchored `strings.HasSuffix` check, the same bug class as CVE-2024-27302 (go-zero `isOriginAllowed`). Any attacker who registers a domain that merely ends with the configured allowed suffix (e.g. `evilremix.com` for an allowlist entry `*.remix.com`) can have their origin reflected in `Access-Control-Allow-Origin`, bypassing the intended subdomain-only CORS restriction on the gateway's user-facing HTTP server.

### Finding Description
The gateway's `HTTPServerConfig.CORSAllowedOrigins` supports wildcard entries like `*.remix.com` [1](#0-0) . Matching is performed by `isAllowedOrigin`, which strips the `*.` prefix from the allowed host and then checks whether the request's `Origin` header host has that string as a suffix, with no requirement that a `.` (or other domain boundary) precede the match: [2](#0-1) 

Because `strings.HasSuffix` performs a raw byte-suffix comparison, a fully separate, attacker-registered domain such as `evilremix.com` satisfies `HasSuffix("evilremix.com", "remix.com")` even though it is not a subdomain of `remix.com`. This is exactly the root cause identified in the go-zero advisory (GHSA-fgxv-gw55-r5fq / CVE-2024-27302), where `isOriginAllowed` used `strings.HasSuffix(origin, o)` without boundary checking.

`isAllowedOrigin` is invoked directly from `handleRequest`, the request handler mounted on the gateway's configurable path for both the `UserServerConfig` and any HTTP server built from `HTTPServerConfig` [3](#0-2) , which is reachable by any unauthenticated client — the JWT/authorization header is only extracted afterwards and passed to the downstream handler, not validated before the CORS decision [4](#0-3) .

### Impact Explanation
If an operator configures a wildcard `CORSAllowedOrigins` entry (e.g. `https://*.mycompany.com`) intending to scope browser access to their own subdomains, an attacker who controls a domain with a matching suffix (e.g. `https://evilmycompany.com` or `https://notmycompany.com`) can have that origin reflected back in `Access-Control-Allow-Origin`. Combined with `Access-Control-Allow-Headers: Content-Type` and the ability to set cookies/auth headers cross-origin, this allows a malicious webpage to make in-browser requests to the gateway's user API on behalf of a victim and read the JSON-RPC responses, defeating the CORS-based isolation the operator configured.

### Likelihood Explanation
Exploitability depends on the operator using a wildcard entry in `CORSAllowedOrigins` (documented/supported feature, see wildcard tests) and on the attacker being able to register/host a domain with the matching suffix — which is realistic and cheap (domain squatting), matching the same low-complexity, no-privilege exploitation profile as the original go-zero advisory (`AV:N/AC:L/PR:N/UI:N`).

### Recommendation
Fix the wildcard suffix comparison to anchor on domain boundaries, e.g. require that the origin host equals the stripped suffix or ends with `"."+allowedHost` instead of a raw `strings.HasSuffix`:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```

### Proof of Concept
1. Configure the gateway user server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. Send a request to the gateway's user HTTP endpoint with header `Origin: https://evilremix.com`.
3. `isAllowedOrigin` strips `*.` to get `remix.com`, then `strings.HasSuffix("evilremix.com", "remix.com")` returns `true` [5](#0-4) .
4. The server responds with `Access-Control-Allow-Origin: https://evilremix.com`, allowing the attacker's page to read the response via browser fetch/XHR, despite `evilremix.com` not being a subdomain of `remix.com`.

### Citations

**File:** core/services/gateway/network/httpserver.go (L53-54)
```go
	CORSEnabled            bool
	CORSAllowedOrigins     []string
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
