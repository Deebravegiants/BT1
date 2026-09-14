## Analog Found: CORS Origin-Allowlist Bypass via Unanchored Suffix Match in Gateway HTTP Server

### Title
CORS wildcard-origin allowlist bypass via unanchored `strings.HasSuffix` domain matching - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The gateway's CORS origin check, `isAllowedOrigin`, validates wildcard-configured allowed origins (e.g. `*.ethereum.org`) by stripping the `*.` prefix and then checking `strings.HasSuffix(originHost, allowedHost)`. This is the same bug class as the referenced Gitingest CVE: a naive prefix/suffix string comparison used as a security boundary without any delimiter/anchor check, allowing an attacker to craft a hostname that satisfies the suffix condition without being a genuine subdomain.

### Finding Description
`isAllowedOrigin` implements wildcard host matching as follows: [1](#0-0) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

For a configured allowlist entry `*.ethereum.org`, `allowedHost` becomes `ethereum.org`. The check then only tests whether `originHost` ends with the literal string `ethereum.org` — it never verifies that the character immediately preceding that suffix is a `.` (a domain-label boundary). Consequently, an attacker-registered domain such as `evilethereum.org` also satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org")`, and is treated as a trusted subdomain of `ethereum.org` even though it is a completely unrelated, attacker-controlled domain. This is called from the gateway's public request handler: [2](#0-1) 

The gateway's HTTP server is the internet-facing entry point that unprivileged/unauthenticated clients hit directly, and `CORSAllowedOrigins` is an operator-configured allowlist meant to restrict which web origins may read cross-origin responses — exactly the "allowlist/subscriptions, handlers" scope for the internet-facing gateway.

### Impact Explanation
If CORS is enabled (`config.CORSEnabled`) and any wildcard entry is configured in `CORSAllowedOrigins`, an attacker who registers a similarly-suffixed domain (e.g. `evilethereum.org` when `*.ethereum.org` is allowed) can host a malicious page there. When a victim's browser visits that page and it issues a request to the gateway, the server reflects the attacker's `Origin` header back in `Access-Control-Allow-Origin`, causing the browser to permit the attacker's script to read the gateway's response cross-origin — an allowlist bypass that leads to cross-user response confusion / unauthorized cross-origin data access, matching the "allowlist bypass" and "cross-user response confusion" impact categories.

### Likelihood Explanation
Exploitation only requires: (1) an operator configuring a wildcard entry in `CORSAllowedOrigins` (a supported, documented pattern per the test suite, e.g. `https://*.ethereum.org`), and (2) an attacker registering a domain with the trusted suffix as a literal string suffix (no subdomain dot required), which is trivial and inexpensive (e.g., `evilethereum.org`, `notethereum.org`). No credentials or privileged access are needed by the attacker — the request originates from a victim's browser visiting an attacker page, i.e., an unprivileged external actor path.

### Recommendation
Anchor the suffix match to the domain-label boundary: require that `originHost` equals `allowedHost` or that it ends with `"."+allowedHost` (e.g. `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`), mirroring how proper hostname allowlists must validate that the match starts at a label boundary rather than an arbitrary substring boundary.

### Proof of Concept
1. Configure gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers/controls `https://evilethereum.org` and hosts a page there that issues a `fetch()`/XHR request to the gateway's HTTP endpoint with `Origin: https://evilethereum.org`.
3. `isAllowedOrigin` computes `allowedHost = "ethereum.org"`, `originHost = "evilethereum.org"`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.
4. The gateway sets `Access-Control-Allow-Origin: https://evilethereum.org`, and the victim's browser allows the attacker's script to read the gateway's response, despite `evilethereum.org` never being an intended subdomain of `ethereum.org`. [3](#0-2)

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
