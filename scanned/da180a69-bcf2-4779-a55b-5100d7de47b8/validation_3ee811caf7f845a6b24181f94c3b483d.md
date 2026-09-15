The strongest reachable analog to the wget SSRF bug class (naive/incorrect host validation allowing an attacker to make a legitimate-looking host string satisfy an allowlist check) is the CORS origin allowlist logic in the gateway's `httpServer.isAllowedOrigin`.

### Title
CORS wildcard-origin allowlist bypass via naive suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's internet-facing HTTP server implements a CORS allowlist that supports wildcard subdomain entries like `*.example.com`. The wildcard match is implemented with a bare `strings.HasSuffix` check, without verifying that the matched suffix is preceded by a domain separator (`.`). This lets an attacker-controlled origin such as `evilexample.com` satisfy an allowlist entry meant only for `example.com` and its subdomains, exactly mirroring the class of bug in CVE-2024-10524 where naive/partial matching of an attacker-influenced string (there, credentials in a shorthand URL; here, a hostname string) causes the target system to treat attacker-controlled input as trusted.

### Finding Description
`isAllowedOrigin` parses the request's `Origin` header and each configured allowed origin with `splitURL`, then compares scheme, port, and finally host [1](#0-0) . For wildcard entries it strips the `*.` prefix and does a raw suffix comparison: [2](#0-1) 

Because `strings.HasSuffix(originHost, allowedHost)` has no boundary check, any origin host that merely *ends with* the configured domain string will match, even when it's a different domain entirely (e.g. `evilexample.com` vs. allowed `*.example.com` → stripped to `example.com` → `HasSuffix("evilexample.com", "example.com")` is `true`). The same applies to sibling-domain confusion patterns like `notexample.com` matching `*.example.com`.

This is invoked from `handleRequest`, the single entry point for all gateway HTTP traffic, which reflects the attacker's `Origin` back via `Access-Control-Allow-Origin` once the check passes [3](#0-2) .

### Impact Explanation
A successful bypass lets a malicious, attacker-registered domain (e.g. `evilexample.com`) be treated as an allowed CORS origin for a gateway operator who intended to allow only `*.example.com`. Browser-based JavaScript running on the attacker's origin can then read the gateway's HTTP responses cross-origin, which is a concrete allowlist-bypass / cross-origin response confusion (matching the accepted impact classes: allowlist bypass and cross-user/cross-origin response confusion). No `Access-Control-Allow-Credentials` header is set in this handler [4](#0-3) , so the practical severity is bounded to responses obtainable without cookies; however, the allowlist itself is still concretely bypassed, and any deployment relying on wildcard entries for access control gets a false sense of restriction.

### Likelihood Explanation
Any external, unprivileged actor can trigger this simply by sending an HTTP request to the gateway's exposed endpoint with a crafted `Origin` header — no authentication or special privilege is required, and CORS wildcard configuration (`CORSAllowedOrigins`) is a documented/supported feature [5](#0-4) .

### Recommendation
Fix `isAllowedOrigin`'s wildcard match to require the suffix be preceded by a `.` (i.e., match only `*.` + `allowedHost` as a full subdomain label, not an arbitrary string suffix), for example by checking `strings.HasSuffix(originHost, "."+allowedHost)` in addition to the exact match, or by splitting on `.` and comparing labels exactly.

### Proof of Concept
1. Configure gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Send a request to the gateway with header `Origin: https://evilexample.com`.
3. `splitURL` yields `originHost = "evilexample.com"`; the wildcard branch strips `*.` from `example.com` and checks `strings.HasSuffix("evilexample.com", "example.com")`, which returns `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilexample.com`, permitting a page hosted on the attacker's unrelated domain to read the gateway's JSON responses via `fetch`/XHR, despite the operator's intent to restrict access to `example.com` subdomains only. [2](#0-1)

### Citations

**File:** core/services/gateway/network/httpserver.go (L53-54)
```go
	CORSEnabled            bool
	CORSAllowedOrigins     []string
```

**File:** core/services/gateway/network/httpserver.go (L157-179)
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
```

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
