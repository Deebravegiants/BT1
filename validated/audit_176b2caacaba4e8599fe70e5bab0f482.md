## Title
CORS origin allowlist bypass via non-label-boundary suffix matching in Gateway HTTP server - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The Gateway's `isAllowedOrigin` function implements wildcard-subdomain matching (`*.example.com`) using a raw `strings.HasSuffix` comparison without verifying a DNS label (dot) boundary. This is the same bug class as CVE-2026-59223 (Open WebUI `WEB_FETCH_FILTER_LIST`): a suffix-string match instead of a proper hostname-label match lets an attacker-controlled domain that merely *ends with* the allowed suffix satisfy the check, even though it is not actually a subdomain of the allowed domain.

### Finding Description
`isAllowedOrigin` parses the request `Origin` header and each configured `CORSAllowedOrigins` entry, then for wildcard entries strips the `*.` prefix and checks: [1](#0-0) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

`strings.HasSuffix(originHost, allowedHost)` matches on raw character suffix, not on DNS label boundaries. If an operator configures `CORSAllowedOrigins: ["https://*.example.com"]` intending to allow only `*.example.com` subdomains, an origin such as `https://evilexample.com` also satisfies `strings.HasSuffix("evilexample.com", "example.com")` because "evilexample.com" literally ends with the string "example.com" — there is no check that the character immediately preceding the match is a `.`.

This mirrors the root cause described in the Open WebUI advisory: matching hostnames with plain string suffix/`endswith` semantics instead of parsed, label-boundary-aware comparison (`host == entry or host.endswith('.' + entry)`).

This function gates `handleRequest` in the same file, which reflects the attacker-supplied `Origin` back into `Access-Control-Allow-Origin` when `isAllowedOrigin` returns true: [2](#0-1) 

### Impact Explanation
The Gateway HTTP server is the internet-facing entry point for Chainlink Functions/DON Gateway requests, reachable by unprivileged/external clients. An administrator configuring `CORSAllowedOrigins: ["https://*.mycompany.com"]` to scope which web origins may make credentialed/cross-origin browser calls to the gateway can be bypassed by any attacker who registers or controls a domain that textually ends with the allowed suffix (e.g., `evilmycompany.com`, or a subdomain-look-alike registered under a different TLD/prefix). The gateway will then set `Access-Control-Allow-Origin` to the attacker's origin, permitting a malicious web page on that origin to issue cross-origin requests to the gateway and read the response — an allowlist-bypass / cross-origin response-exposure issue.

### Likelihood Explanation
Exploitation requires only registering/controlling a domain whose name ends with the configured allowed suffix (no special network position, no privileged credentials) and getting a victim's browser to visit a page on that domain while the gateway API is reachable — this is a low-effort, purely client-side attack against any deployment using wildcard `CORSAllowedOrigins` entries.

### Recommendation
Match `originHost` against the wildcard suffix using a label-boundary check rather than raw string suffix comparison, e.g.:

```go
allowedHost = allowedHost[2:]
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```

This ensures `evilexample.com` cannot satisfy `*.example.com`, while `foo.example.com` still correctly matches.

### Proof of Concept
1. Gateway configured with `CORSAllowedOrigins: ["https://*.example.com"]`.
2. Attacker hosts a page at `https://evilexample.com`.
3. Browser sends `Origin: https://evilexample.com` in a request to the gateway's configured path.
4. `isAllowedOrigin` strips `*.` → `allowedHost = "example.com"`; `strings.HasSuffix("evilexample.com", "example.com")` returns `true`.
5. Server responds with `Access-Control-Allow-Origin: https://evilexample.com`, letting the attacker's page read the cross-origin response, defeating the operator's intended subdomain-only allowlist — analogous to the `is_string_allowed`/`endswith` bypass in the referenced Open WebUI advisory. [3](#0-2)

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
