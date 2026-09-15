### Title
CORS Origin Allowlist Bypass via Improper Suffix Matching in Gateway Wildcard Origin Check - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's internet-facing HTTP server implements a custom CORS origin allowlist check (`isAllowedOrigin`) that supports wildcard subdomain entries (e.g. `*.remix.com`). The wildcard match uses `strings.HasSuffix` on the raw hostname string without enforcing a dot (`.`) boundary before the allowed suffix, allowing an attacker-controlled domain that merely ends with the allowed suffix (with no separating dot) to be treated as a trusted subdomain.

### Finding Description
`isAllowedOrigin` parses the client-supplied `Origin` header via `splitURL` and compares it against each entry in `s.config.CORSAllowedOrigins`: [1](#0-0) 

The vulnerable wildcard branch is: [2](#0-1) 

If an operator configures an allowed origin such as `*.remix.com` (intended to permit only `foo.remix.com`, `bar.remix.com`, etc.), the code strips the `*.` prefix leaving `remix.com`, then checks `strings.HasSuffix(originHost, "remix.com")`. This check has no boundary validation — a hostname like `evilremix.com` (attacker-registered domain) also satisfies `strings.HasSuffix("evilremix.com", "remix.com") == true`, even though it is not a subdomain of `remix.com` at all. The `Origin` header is fully attacker-controlled and sent from any unprivileged browser client making a cross-origin request to the gateway's HTTP handler, which is invoked in `handleRequest`: [3](#0-2) 

When the check passes, the server reflects the attacker's origin back in `Access-Control-Allow-Origin`, permitting a malicious webpage on `evilremix.com` to make authenticated cross-origin requests to the gateway and read the response, defeating the purpose of the allowlist.

### Impact Explanation
This is a concrete allowlist-bypass on the internet-facing gateway's request handler. An attacker who registers a domain sharing a suffix with a configured wildcard entry (e.g., `notremix.com`, `evilremix.com`) can have their origin treated as trusted, enabling cross-origin browser requests against the gateway from a page the operator did not intend to trust. Depending on what the gateway handler processes (message envelopes, JWT-authenticated capability requests, etc.), this could lead to cross-user response exposure or unauthorized request submission from a browser context that should have been blocked by CORS.

### Likelihood Explanation
Exploitation requires: (1) the operator has configured at least one wildcard `CORSEnabled`/`CORSAllowedOrigins` entry, and (2) the attacker can register or control a domain that string-matches the suffix without a proper subdomain boundary. Domain registration is trivial and cheap, and wildcard CORS entries are a documented, supported configuration option (see `sample_config.toml`), so this is realistically triggerable by any unprivileged web attacker once such a config is in use.

### Recommendation
Fix the wildcard suffix check to require a `.` boundary (or full label match) before the allowed suffix, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This ensures `evilremix.com` does not match `*.remix.com`, while `sub.remix.com` still does.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["*.remix.com"]`.
2. From an unprivileged client, send an HTTP request to the gateway's request path with header `Origin: https://evilremix.com`.
3. Observe that `isAllowedOrigin` returns `true` (since `strings.HasSuffix("evilremix.com", "remix.com")` is true), and the server responds with `Access-Control-Allow-Origin: https://evilremix.com`, allowing a page hosted on `evilremix.com` to make credentialed cross-origin requests to the gateway that should have been rejected. [1](#0-0)

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
