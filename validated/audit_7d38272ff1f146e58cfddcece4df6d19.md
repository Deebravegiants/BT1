### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's `httpServer.isAllowedOrigin` function implements wildcard-domain matching for the `CORSAllowedOrigins` allowlist (e.g. `*.remix.com`), but it uses an unanchored `strings.HasSuffix` comparison instead of checking that a subdomain boundary (a literal `.`) precedes the allowed suffix. This lets an attacker register any domain that merely ends with the allowed suffix as a string (e.g. `evilremix.com`) and have it accepted as an allowed origin for `*.remix.com`, defeating the intent of the wildcard allowlist entry.

### Finding Description
`isAllowedOrigin` parses the incoming `Origin` header and, for each configured allowed origin, checks scheme/port equality and then host matching: [1](#0-0) 

For wildcard entries the code strips the `*.` prefix and does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

`strings.HasSuffix(originHost, allowedHost)` only checks that `originHost` ends with the literal characters of `allowedHost`; it does not require a `.` (or start-of-string) immediately before that suffix. This is precisely the same class of bug described in the external report: a whitelist check that is supposed to scope access to a specific set (subdomains of `remix.com`) is instead conflated with a broader, unintended set (any hostname string ending in `remix.com`), silently and unintentionally widening what is allowed — mirroring how the HubPool's route-whitelist granularity mismatch silently widened rebalancing permissions to unintended routes.

Concretely, for an allowlist entry `https://*.remix.com`, `allowedHost` becomes `remix.com`. An origin such as `https://evilremix.com` or `https://attacker-remix.com` will satisfy `strings.HasSuffix("evilremix.com", "remix.com") == true` and be treated as an allowed subdomain of `remix.com`, even though it is a completely unrelated, attacker-controlled domain.

This function directly gates the CORS response headers on the internet-facing gateway HTTP server (`handleRequest` calls `isAllowedOrigin` to decide whether to echo `Access-Control-Allow-Origin` for the caller's `Origin`), which is reachable by any unprivileged remote client capable of sending an HTTP request with a crafted `Origin` header.

### Impact Explanation
If `Access-Control-Allow-Origin` is echoed back based on this flawed check (and especially if combined with `Access-Control-Allow-Credentials`), a malicious website hosted on a domain like `evilremix.com` can make cross-origin browser requests to the gateway that the operator intended to restrict to genuine `*.remix.com` subdomains, potentially reading authenticated/cross-user responses in a victim's browser session. This is an allowlist-bypass issue in the internet-facing gateway's origin/allowlist handling.

### Likelihood Explanation
Exploitation only requires registering an attacker-controlled domain string that happens to end with the configured allowed suffix (e.g., buying `evilremix.com` when `*.remix.com` is allowlisted) and getting a victim to load a page from that domain while their browser holds a session/credentials for the gateway. No privileged access or node/peer compromise is required — this is purely a client-side/unprivileged-actor attack against the allowlist check.

### Recommendation
Anchor the wildcard suffix match on a domain boundary rather than a raw string suffix, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".remix.com"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` either equals the base domain or ends with `.` + the base domain, preventing `evilremix.com` from matching `*.remix.com` while still allowing legitimate subdomains like `foo.remix.com`.

### Proof of Concept
1. Configure the gateway with `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. Send an HTTP request to the gateway's endpoint with header `Origin: https://evilremix.com`.
3. `isAllowedOrigin` computes `allowedHost = "remix.com"` and `originHost = "evilremix.com"`; `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`.
4. The gateway responds with `Access-Control-Allow-Origin: https://evilremix.com`, incorrectly treating the attacker's domain as an allowed subdomain of `remix.com`.

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
