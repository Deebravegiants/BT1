## Analysis

The Gateway's CORS origin allowlist check contains exactly the hostname-matching bug class described in the advisory: it validates a "trusted" endpoint (allowed CORS origin) using unbounded string matching instead of a proper domain-boundary check.

### Root cause [1](#0-0) 

```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	...
	for _, allowed := range s.config.CORSAllowedOrigins {
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
		...
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

For a wildcard allow-entry like `https://*.ethereum.org`, the code strips the `*.` and then only checks `strings.HasSuffix(originHost, "ethereum.org")` [2](#0-1) . There is no check that the character immediately preceding the suffix is a `.` (a domain-label boundary). This means an attacker-controlled origin such as `https://evilethereum.org` also satisfies `HasSuffix("evilethereum.org", "ethereum.org")`, so it is treated as a trusted subdomain of `ethereum.org` even though it is a completely unrelated, attacker-registrable domain. This mirrors the advisory's bug class: a "trusted" hostname check that matches on a substring/prefix/suffix instead of validating the actual host boundary.

The result of `isAllowedOrigin` directly gates whether the Gateway reflects `Access-Control-Allow-Origin` for the requesting origin, exposing the JSON-RPC style handler responses to that origin's browser context [3](#0-2) .

### Title
CORS wildcard origin allowlist bypass via unbounded hostname suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
`httpServer.isAllowedOrigin` implements wildcard CORS origin matching (`*.example.com`) using a bare `strings.HasSuffix` check on the origin's hostname without verifying a label/dot boundary before the matched suffix, allowing any domain that merely ends with the configured suffix (e.g. `evilexample.com` matching a `*.example.com` allow-entry) to be treated as trusted.

### Finding Description
`isAllowedOrigin` parses both the incoming `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port. When an allow-entry starts with `*.`, the code strips the `*.` prefix and performs `strings.HasSuffix(originHost, allowedHost)` [4](#0-3) . This check is purely string-based: it does not require that the character preceding the matched suffix be a `.` separator. Consequently, a domain like `evilethereum.org` (attacker-registered) will pass the check for an operator's intended `*.ethereum.org` allowlist entry, because `"evilethereum.org"` ends with the literal string `"ethereum.org"`.

### Impact Explanation
An unprivileged, unauthenticated web attacker who registers or controls a domain sharing the allowlisted suffix (no leading dot required) can serve a page from that domain and make cross-origin browser requests against the Gateway's HTTP endpoint. Because `isAllowedOrigin` incorrectly returns `true`, the server reflects `Access-Control-Allow-Origin` for the attacker's origin [5](#0-4) , letting the attacker's browser-side JavaScript read Gateway JSON-RPC responses that were only intended to be readable by the operator's legitimate trusted subdomains — an allowlist bypass at the gateway boundary.

### Likelihood Explanation
Exploitation only requires registering/controlling a domain name that happens to end with the configured trusted suffix (e.g., buying `evil-ethereum.org` or `notethereum.org`-style names, or any domain an attacker controls that shares the tail string) and getting a victim to visit a page served from it while their browser has access to the Gateway. No credentials or privileged position are needed — this is reachable directly from any unprivileged client on the internet-facing gateway.

### Recommendation
Change the wildcard match to require a proper subdomain boundary, e.g. `strings.HasSuffix(originHost, "."+allowedHost)` (or equivalently check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`), so that only genuine subdomains of the configured base domain are matched.

### Proof of Concept
1. Operator configures `CORSAllowedOrigins: ["https://*.ethereum.org"]`.
2. Attacker registers/controls `evilethereum.org` and serves a page from `https://evilethereum.org`.
3. Victim's browser (with network access to the Gateway) loads the attacker page, which issues a fetch to the Gateway endpoint with `Origin: https://evilethereum.org`.
4. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and evaluates `strings.HasSuffix("evilethereum.org", "ethereum.org")` → `true`, so the server sets `Access-Control-Allow-Origin: https://evilethereum.org` [5](#0-4) , letting the attacker page read the Gateway's response, defeating the intended origin allowlist.

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
