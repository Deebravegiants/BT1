### Title
CORS wildcard origin allowlist bypass via unanchored suffix match - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Gateway HTTP server's CORS origin check treats a wildcard allow-entry like `*.remix.com` as "any host that *ends with* `remix.com`" instead of "any host that is a subdomain of `remix.com`". This is the same bug class as CVE-2018-18966: an allowlist/blocklist check is applied on a substring/suffix basis without validating the boundary, so an attacker-controlled value that is textually similar to (but not actually) the intended trusted value slips through the filter.

### Finding Description
`isAllowedOrigin` parses the incoming `Origin` header and compares it against each entry in `CORSAllowedOrigins`. For wildcard entries it strips the `*.` prefix and does: [1](#0-0) 

`strings.HasSuffix(originHost, allowedHost)` has no boundary check for a preceding `.`. So if the operator configures `*.remix.com`, `allowedHost` becomes `remix.com`, and an attacker origin such as `evil-remix.com` or `attackerremix.com` also satisfies `HasSuffix(originHost, "remix.com")`, even though it is not a subdomain of `remix.com` at all.

This check gates `handleRequest`, which reflects the attacker-supplied `Origin` value back verbatim into `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true: [2](#0-1) 

### Impact Explanation
Any unprivileged actor who can serve a page from a domain that merely ends with the configured allowlisted suffix (e.g. registering `evil-remix.com` when the operator intended to allow only `*.remix.com`) can have their origin reflected as an allowed CORS origin on the Gateway's internet-facing HTTP endpoint. Browsers making cross-origin `fetch`/XHR calls to the Gateway from that attacker-controlled origin would then be permitted by the browser to read the Gateway's JSON-RPC responses (workflow triggers, vault-adjacent flows, etc., depending on which handler is behind this HTTP server), which is a cross-origin response confusion / allowlist-bypass class issue matching the CVE's "incomplete blacklist/allowlist boundary" bug pattern.

### Likelihood Explanation
Exploitability depends entirely on the gateway operator configuring a wildcard entry in `CORSAllowedOrigins` (e.g. `*.example.com`). Given wildcard CORS configuration is a documented/expected feature (see the code's own wildcard-handling comment), and domain registration of suffix-colliding names is trivial and cheap for an attacker, likelihood is non-trivial wherever wildcard CORS entries are used in production Gateway deployments.

### Recommendation
Anchor the suffix match on a full-label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".remix.com" (keep the dot)
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `evil-remix.com` no longer matches `*.remix.com`, since `strings.HasSuffix("evil-remix.com", ".remix.com")` is false, while `foo.remix.com` still matches.

### Proof of Concept
1. Operator configures Gateway with `CORSAllowedOrigins = ["https://*.remix.com"]` and `CORSEnabled = true`.
2. Attacker registers/serves a page at `https://evil-remix.com` (or `https://attackerremix.com`).
3. Attacker's page issues a cross-origin `fetch()` to the Gateway's HTTP endpoint with `Origin: https://evil-remix.com`.
4. `isAllowedOrigin` computes `allowedHost = "remix.com"` and evaluates `strings.HasSuffix("evil-remix.com", "remix.com")` → `true`, so the request is treated as allowed.
5. The server sets `Access-Control-Allow-Origin: https://evil-remix.com` in the response, letting the attacker's browser-side JavaScript read the Gateway's response body cross-origin, even though `evil-remix.com` was never intended to be trusted.

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
