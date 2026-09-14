### Title
CORS origin allowlist bypass via unanchored suffix matching in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's HTTP server uses a permissive substring/suffix check to validate the `Origin` header against configured wildcard CORS entries. Because the check only verifies that the origin *ends with* the configured domain string — without requiring a preceding dot (label boundary) — an attacker who registers any domain that happens to end with the same characters as an allowlisted domain can be treated as an allowed, trusted origin. This mirrors the Pixeldrain bug class: a security-relevant "is this host our trusted service" decision is made via loose substring matching instead of exact/boundary-aware comparison, which lets an unrelated third-party host slip through and receive privileged treatment (here, cross-origin access grants) intended only for the legitimate domain.

### Finding Description
`isAllowedOrigin` splits both the incoming `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port, then for wildcard entries (`*.example.com`) strips the `*.` prefix and does: [1](#0-0) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

`strings.HasSuffix(originHost, allowedHost)` has no label-boundary check (no requirement that the character immediately preceding the suffix be a literal `.`). Any attacker-registered domain whose name simply ends with the same character sequence — e.g. `evilremix.com` or `notremix.com` for an allowlist entry `*.remix.com` — satisfies `HasSuffix("evilremix.com", "remix.com") == true`, even though it is not a subdomain of `remix.com` at all.

This function gates `handleRequest`'s CORS response: [2](#0-1) 

When `isAllowedOrigin` incorrectly returns true, the server sets `Access-Control-Allow-Origin: <attacker origin>` and permits the browser-side JS on the attacker's page to make cross-origin requests to the Gateway's public, internet-facing HTTP endpoint (the same endpoint that forwards JSON-RPC requests carrying JWT/allowlist-based auth into `ProcessRequest`) and read the responses, exactly as if it were on the trusted subdomain.

### Impact Explanation
An unprivileged actor who registers a domain string ending in the same substring as a legitimate allowlisted host (a cheap, unrestricted action — domain registrars do not prevent registering `notremix.com` next to `remix.com`) can have their site treated as a trusted CORS origin by the Gateway. Any user who is logged into the legitimate application/DON UI and is lured to the malicious look-alike domain can have browser-issued cross-origin requests (and their JSON responses, including auth-bearing JSON-RPC responses processed via `handleRequest`/`ProcessRequest`) read by the attacker's page. This is a concrete allowlist bypass on the internet-facing gateway component, matching the report's bug class of "loose host matching leaking privileged treatment to a look-alike unverified host."

### Likelihood Explanation
Exploitation requires only registering an inexpensive domain that lexically ends with the configured allowlisted suffix and getting a victim (who already has legitimate session/auth material for the Gateway) to visit or be redirected to it. No compromise of Chainlink infrastructure is needed; the operator's own `CORSAllowedOrigins` configuration (e.g., `*.remix.com`) is the only input, and the flaw is purely in the client-supplied `Origin` header comparison logic, which is fully attacker-controlled.

### Recommendation
Replace the unanchored `strings.HasSuffix` check with a boundary-aware comparison, e.g. require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`, so that only true subdomains of the allowlisted domain (separated by a literal dot) are accepted.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. From a browser page hosted at `https://evilremix.com` (a domain the attacker legitimately registered), send a fetch/XHR request to the Gateway's configured `Path` endpoint with header `Origin: https://evilremix.com`.
3. `splitURL` parses `originHost = "evilremix.com"`, `allowedHost` becomes `"remix.com"` after stripping `*.`.
4. `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`, so `isAllowedOrigin` returns `true` and the server responds with `Access-Control-Allow-Origin: https://evilremix.com`, granting the attacker's origin the same cross-origin access as a genuine `*.remix.com` subdomain.

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
