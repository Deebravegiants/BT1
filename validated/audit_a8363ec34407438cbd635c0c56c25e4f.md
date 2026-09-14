### Title
CORS Origin Allowlist Bypass via Improper Suffix Check in Gateway `isAllowedOrigin` - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's HTTP server validates the browser-supplied `Origin` header against an operator-configured `CORSAllowedOrigins` list using `isAllowedOrigin()`. For wildcard entries (e.g. `*.ethereum.org`), the check strips the `*.` prefix and then performs an unanchored `strings.HasSuffix` comparison instead of verifying a proper subdomain boundary (a preceding `.`). This mirrors the root cause of the referenced advisory (Jupyter Server's unanchored `re.match()` origin check): a suffix/prefix string match without boundary anchoring lets an attacker-registered domain that merely *ends with* the allowed suffix satisfy the check, even though it is not a legitimate subdomain.

### Finding Description
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements the wildcard branch as: [1](#0-0) 

Given an allowlist entry `https://*.ethereum.org`, `allowedHost` becomes `ethereum.org` after stripping `*.`. The subsequent check `strings.HasSuffix(originHost, allowedHost)` returns `true` for any `originHost` that ends in the literal string `ethereum.org`, regardless of whether a `.` subdomain separator precedes it. An attacker who registers a domain such as `evil-ethereum.org` or `notethereum.org` (no dot boundary) would pass this check, because `HasSuffix("evil-ethereum.org", "ethereum.org")` is `true` even though `evil-ethereum.org` is an entirely different, attacker-controlled domain rather than a subdomain of `ethereum.org`.

The result feeds directly into the CORS response: [2](#0-1) 

`handleRequest` reflects the attacker's `Origin` header back in `Access-Control-Allow-Origin` whenever `isAllowedOrigin` returns `true`, so a script served from the attacker's spoofed domain can make cross-origin browser requests to the Gateway endpoint and read the JSON responses (job/DON call results returned by `HTTPRequestHandler.ProcessRequest`) that would otherwise be restricted to the legitimate allowlisted origins.

### Impact Explanation
This is an unprivileged-client-reachable allowlist bypass on the internet-facing Gateway HTTP server. An attacker only needs to register a domain string that happens to end in an operator-trusted suffix (no subdomain relationship required) to have their web page's cross-origin requests treated as coming from a trusted origin. This breaks the intended origin-based access boundary for the Gateway API and can expose response data (e.g., DON/capability call results routed through the Gateway) to pages hosted on attacker-controlled infrastructure that were never intended to be trusted, which is a cross-user/cross-origin response confusion issue.

### Likelihood Explanation
Exploitation requires only that the operator's `CORSAllowedOrigins` config contains at least one wildcard entry (a common and documented pattern, as shown by the wildcard test cases), and that the attacker register/control a domain ending in the same suffix (no dot boundary needed) — a low-cost, purely domain-registration action requiring no special privileges, network position, or insider access.

### Recommendation
Fix the wildcard match to enforce a proper subdomain boundary, e.g. require the character immediately preceding the suffix to be `.`:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This ensures only true subdomains (or the bare domain) of the allowed host match, closing the bypass.

### Proof of Concept
1. Configure the Gateway with `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser page hosted at `https://evil-ethereum.org` (or any domain ending in `ethereum.org` without a `.` separator), send a fetch/XHR request to the Gateway's configured path with header `Origin: https://evil-ethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` (via `strings.HasSuffix("evil-ethereum.org", "ethereum.org")`), so the server responds with `Access-Control-Allow-Origin: https://evil-ethereum.org`, allowing the attacker page's JavaScript to read the Gateway's JSON response cross-origin, despite `evil-ethereum.org` not being an intended subdomain of `ethereum.org`.

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
