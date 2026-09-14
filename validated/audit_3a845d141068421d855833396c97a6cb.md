## Analysis

The chainlink gateway's CORS origin allowlist check (`isAllowedOrigin` in `core/services/gateway/network/httpserver.go`) is the closest structural analog to the authentik `wreply` bug: both use a substring-based match (`HasPrefix`/`HasSuffix`) instead of a proper domain-boundary check, letting an attacker-controlled host satisfy the "trusted" pattern. This is a real, reachable bug in the internet-facing gateway HTTP allowlist path, so it qualifies under the rules.

### Title
CORS wildcard origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway HTTP server's wildcard CORS-origin matching uses `strings.HasSuffix` without verifying a domain-label boundary (a preceding `.`), so a wildcard entry like `*.ethereum.org` also matches unrelated attacker-registered domains such as `evilethereum.org`, causing the server to reflect the attacker's `Origin` header as `Access-Control-Allow-Origin`.

### Finding Description
`isAllowedOrigin` splits both the request `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port via `splitURL`, then for wildcard entries (`*.domain`) strips the `*.` prefix and checks: [1](#0-0) 

`strings.HasSuffix(originHost, allowedHost)` only checks that `originHost` ends with the literal string `allowedHost` — it does not require that the character immediately preceding that suffix be a `.` (a domain-label boundary). Consequently, for an allowlist entry `*.ethereum.org` (which strips to `ethereum.org`), a request `Origin` of `https://evilethereum.org` (an entirely different, attacker-registered domain) also satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org")`, and the function returns `true`.

This mirrors the authentik root cause: validating an attacker-influenced value with a raw string containment/prefix/suffix check instead of proper URL/domain parsing that respects component boundaries.

The result is used directly in `handleRequest` to set CORS response headers: [2](#0-1) 

which reflects the attacker's own `Origin` value back as `Access-Control-Allow-Origin`, telling the browser that scripts running on `evilethereum.org` are permitted to read the gateway's HTTP response for cross-origin requests.

### Impact Explanation
An unprivileged, unauthenticated network attacker who registers any domain name ending in the same label string as a configured wildcard allow-pattern (e.g., `notethereum.org`, `evilethereum.org` for `*.ethereum.org`) can host a webpage that makes cross-origin requests to the gateway's public HTTP endpoint and have the browser expose the JSON response to that page's JavaScript, defeating the operator's intended origin allowlist/CORS policy for the gateway API. This is an allowlist bypass on the gateway's internet-facing entry point as called out in scope.

### Likelihood Explanation
Exploitation only requires: (1) the gateway operator configures a wildcard CORS entry (a documented, supported configuration pattern per the tests at `core/services/gateway/network/httpserver_test.go`), and (2) the attacker registers/controls any domain that happens to end with the same suffix string. No credentials, no privileged access, and no interaction beyond visiting an attacker page are needed, making this reasonably likely wherever wildcard CORS entries are used.

### Recommendation
Fix the wildcard match to require a true subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This ensures `evilethereum.org` no longer matches `*.ethereum.org`, while `foo.ethereum.org` still does.

### Proof of Concept
1. Configure the gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = []string{"https://*.ethereum.org"}`.
2. From a browser on `https://evilethereum.org`, send a cross-origin request to the gateway endpoint with header `Origin: https://evilethereum.org`.
3. Observe `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`, and the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker page's script to read the gateway response cross-origin — even though `evilethereum.org` is not a subdomain of `ethereum.org`. [3](#0-2)

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
