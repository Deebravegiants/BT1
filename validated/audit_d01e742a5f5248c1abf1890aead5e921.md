### Title
Wildcard CORS origin allowlist bypass via unbounded suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's user-facing HTTP server implements a wildcard CORS origin check that uses an unanchored `strings.HasSuffix` comparison instead of verifying a proper domain-label boundary. This allows an attacker to craft an `Origin` header value that satisfies a `*.example.com`-style allowlist entry without actually being a subdomain of `example.com`, bypassing the intended hostname allowlist — the same bug class as CVE-2021-26539 (hostname whitelist bypass via malformed/attacker-controlled hostname matching), though reached via string-suffix confusion rather than IDN normalization.

### Finding Description
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` parses the incoming `Origin` header and compares it against each configured `CORSAllowedOrigins` entry: [1](#0-0) 

For wildcard entries (`*.example.com`), the code strips the `*.` prefix and then only checks:
```go
if strings.HasSuffix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

This check does not require a `.` boundary between the attacker-controlled prefix and the allowed suffix. Consequently, any origin hostname that merely ends with the same character sequence as the allowed domain — e.g. `evilexample.com` or `notexample.com` for an allowlist entry `*.example.com` — passes the check, even though it is not a subdomain of `example.com` at all; it is a completely different, attacker-registered domain. This mirrors the root cause of CVE-2021-26539, where a permissive/naive hostname-string comparison (rather than a structurally correct domain match) let an attacker-supplied hostname slip past an intended allowlist.

The `Origin` request header is fully attacker-controlled by any client making a cross-origin browser request — an unprivileged actor.

### Impact Explanation
When `isAllowedOrigin` returns true, the server reflects the (attacker-supplied) `Origin` value into `Access-Control-Allow-Origin` and sets `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`, enabling that origin's page to make cross-origin GET/POST requests to the Gateway's `/user` endpoint and read the response: [3](#0-2) 

If an operator configures a wildcard entry intending to scope trust to genuine subdomains of a domain they control (e.g. `*.mycompany.com`), an attacker who registers a look-alike domain (`evilmycompany.com`, `notmycompany.com`) can have their web page's script bypass the CORS allowlist entirely and interact with the Gateway API as if it were a trusted subdomain. This is a concrete allowlist-bypass condition on an internet-facing gateway component.

### Likelihood Explanation
Exploitation only requires registering an arbitrary domain whose string happens to end with the allowed suffix and hosting a page that sends a cross-origin request with a spoofed `Origin` header value — something entirely within an unprivileged remote attacker's control, no compromise of the legitimate domain is needed. The only precondition is that the deploying operator uses a wildcard entry in `CORSAllowedOrigins` (a documented, supported configuration pattern), which is plausible for any operator that wants to scope access to a family of subdomains.

### Recommendation
Fix the wildcard matching in `isAllowedOrigin` to require an explicit domain-label boundary, e.g. verify `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)` after stripping the `*.` prefix, rather than a bare `strings.HasSuffix` comparison. Consider replacing manual string splitting with a vetted URL/host parsing and domain-suffix comparison library to avoid similar boundary errors in the future.

### Proof of Concept
1. Operator configures Gateway `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Attacker hosts a page on `https://evilexample.com` and issues a `fetch()`/XHR request to the Gateway's `/user` endpoint with header `Origin: https://evilexample.com`.
3. In `isAllowedOrigin`, `allowedHost` becomes `example.com` after stripping `*.`; `originHost` is `evilexample.com`. `strings.HasSuffix("evilexample.com", "example.com")` evaluates to `true`, so the function returns `true`.
4. The server sets `Access-Control-Allow-Origin: https://evilexample.com`, and the attacker's page can read the JSON-RPC response from the Gateway, despite `evilexample.com` never being a subdomain of `example.com`.

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
