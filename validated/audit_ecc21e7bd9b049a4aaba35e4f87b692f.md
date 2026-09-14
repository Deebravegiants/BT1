## Finding: CORS origin allowlist bypass via improper suffix matching [1](#0-0) 

### Title
CORS Origin Allowlist Bypass via Unanchored Suffix Match - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's wildcard CORS origin allowlist check uses `strings.HasSuffix` without verifying a `.` (dot) boundary before the matched suffix, allowing an attacker-registered domain that merely *ends with* the same characters as an allowed domain (not a true subdomain) to pass the allowlist check and receive a reflected `Access-Control-Allow-Origin` header.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard entry (e.g. `*.ethereum.org` → `ethereum.org`) and then checks `strings.HasSuffix(originHost, allowedHost)`: [2](#0-1) 

This has no boundary check for a preceding `.`, so a domain like `evilethereum.org` or `notethereum.org` (which is not a subdomain of `ethereum.org` at all) satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org")` and is incorrectly treated as an allowed origin. The unprivileged caller fully controls the `Origin` request header value, and the result is reflected verbatim into the response: [3](#0-2) 

This is the same root-cause class as the reported CVE: attacker-controlled input (the `Origin` header, analogous to the `cfg` parameter) is insufficiently validated before being echoed into an HTTP response header/allowlist decision, allowing an attacker-controlled value to be trusted where it should have been rejected.

### Impact Explanation
The `CORSAllowedOrigins` list is the gateway's explicit allowlist mechanism for cross-origin browser access. A domain that is not a genuine subdomain of any trusted entry (e.g. a domain purchased/controlled by an attacker such as `evilethereum.org`) can spoof the check and cause the gateway to respond with `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, and `Access-Control-Allow-Headers: Content-Type`. Any browser-based client that can be lured to such an attacker-controlled page could then have in-browser script issue cross-origin requests to the gateway and read the JSON-RPC responses, which is a bypass of the intended origin allowlist protecting the internet-facing gateway endpoint.

### Likelihood Explanation
Exploitation only requires registering/controlling a domain string that ends with a configured wildcard suffix (no dot required) and sending an `Origin` header with that value from a browser context — no privileges on the chain, node, or gateway are needed. This is directly reachable by any unprivileged web client interacting with `handleRequest`.

### Recommendation
Fix the wildcard match to require a `.` boundary, e.g. verify `strings.HasSuffix(originHost, "."+allowedHost)` (or split on `.` and compare labels) instead of a raw, unanchored `strings.HasSuffix` check, so that only true subdomains (`foo.ethereum.org`) match, not lookalike domains (`evilethereum.org`).

### Proof of Concept
1. Configure gateway with `CORSAllowedOrigins: ["https://*.ethereum.org"]`.
2. From a browser page hosted on `https://evilethereum.org`, send a cross-origin request to the gateway with header `Origin: https://evilethereum.org`.
3. Observe the gateway responds with `Access-Control-Allow-Origin: https://evilethereum.org` (per `isAllowedOrigin` logic at lines 184-190), even though `evilethereum.org` is not a subdomain of `ethereum.org`, confirming the allowlist bypass.

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
