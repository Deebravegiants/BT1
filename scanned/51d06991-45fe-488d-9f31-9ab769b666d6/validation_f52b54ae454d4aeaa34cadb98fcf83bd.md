### Title
CORS Origin Allowlist Wildcard Subdomain Bypass via Improper Suffix Matching - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's CORS origin validation in `isAllowedOrigin` uses a bare `strings.HasSuffix` check to implement wildcard (`*.domain.com`) matching, without verifying that a `.` boundary precedes the matched suffix. This lets an attacker register any domain that merely ends with the configured suffix string (e.g. `evilremix.com` when the allowlist contains `*.remix.com`) and be treated as an authorized subdomain, bypassing the origin allowlist that protects the gateway's internet-facing HTTP endpoint.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard entry and then checks only `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

Because `HasSuffix` performs a raw string-suffix comparison with no dot-boundary check, any origin host that ends with the literal characters of `allowedHost` satisfies the wildcard, regardless of whether it is actually a subdomain. For example, if `CORSAllowedOrigins` contains `https://*.remix.com`, then `allowedHost` becomes `remix.com`, and an attacker-controlled origin such as `https://evilremix.com` or `https://notremix.com` will incorrectly match, since both strings end with `remix.com`.

This mirrors the bug class in CVE-2024-0753 (HSTS subdomain bypass due to imprecise host/subdomain matching): a security allowlist meant to scope trust to genuine subdomains is bypassed by any domain sharing a suffix, letting an unrelated, attacker-registered domain impersonate an authorized subdomain.

`isAllowedOrigin` gates the `Access-Control-Allow-Origin` response header set in `handleRequest`, which is the entry point for all requests to the gateway's public, internet-facing HTTP API (message envelopes to `ProcessRequest`): [2](#0-1) 

### Impact Explanation
If an operator configures a wildcard CORS entry (e.g. `*.mycompany.com`) intending to scope browser access to legitimate subdomains, an unprivileged external attacker who registers a domain merely sharing that suffix (`evilmycompany.com`, `attacker-mycompany.com`) can have their web page's cross-origin requests to the gateway accepted with `Access-Control-Allow-Origin` reflecting their origin. This allows a browser-based attacker to make authenticated cross-origin calls against the gateway on behalf of a victim's browser session/cookies (if any), or otherwise interact with the gateway HTTP API as if from a trusted origin, undermining the intended origin-based access restriction on the gateway's internet-facing surface.

### Likelihood Explanation
Exploitation requires only that the gateway operator configure a wildcard `CORSAllowedOrigins` entry (a documented, supported configuration pattern) and that an attacker register/control a domain sharing the suffix — a low-cost, purely external action requiring no privileges on the Chainlink node or network. No mocking or internal access is needed; this is directly reachable via a normal cross-origin browser request to the gateway's public HTTP listener.

### Recommendation
Fix the wildcard match to enforce a dot boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // keep the leading dot, e.g. ".remix.com"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` must either equal the base domain or end with `.` + the base domain, preventing suffix-only matches like `evilremix.com` against `remix.com`.

### Proof of Concept
1. Configure the gateway with `CORSEnabled: true` and `CORSAllowedOrigins: ["https://*.remix.com"]`.
2. From a browser, load an attacker-controlled page hosted at `https://evilremix.com`.
3. Have the page issue a `fetch` request to the gateway's HTTP endpoint with `Origin: https://evilremix.com`.
4. `isAllowedOrigin` computes `allowedHost = "remix.com"` and evaluates `strings.HasSuffix("evilremix.com", "remix.com")`, which returns `true`, so the gateway responds with `Access-Control-Allow-Origin: https://evilremix.com`, granting the untrusted origin CORS access intended only for genuine `*.remix.com` subdomains.

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
