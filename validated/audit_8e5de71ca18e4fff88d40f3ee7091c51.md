### Title
Improper Wildcard CORS Origin Validation Allows Origin Allowlist Bypass - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's user-facing HTTP server validates `Origin` headers against `CORSAllowedOrigins` using a naive suffix check for wildcard entries (`*.example.com`). Because the match is a plain `strings.HasSuffix` without enforcing a `.` label boundary, an attacker-controlled origin such as `evilexample.com` (no dot) is incorrectly treated as a match for the wildcard pattern `*.example.com`, exactly mirroring the FreeRDP `tls_match_hostname()` bug class where a wildcard suffix match accepts hosts it should reject.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard entry and then checks `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

If an operator configures `CORSAllowedOrigins = ["https://*.example.com"]`, intending to allow only subdomains of `example.com`, the code computes `allowedHost = "example.com"` and then accepts any `originHost` that merely ends with the literal string `example.com`. There is no check that the character preceding the suffix is a `.` (label separator). Consequently, hostnames like `evilexample.com`, `notexample.com`, or `attacker-example.com` all satisfy `strings.HasSuffix(originHost, "example.com")` and are incorrectly treated as trusted, even though they are neither `example.com` nor a genuine subdomain of it.

This is invoked from `handleRequest`, which is the entry point for every request to the gateway's public HTTP API: [2](#0-1) 

When `isAllowedOrigin` returns true, the server echoes the attacker's `Origin` value back in `Access-Control-Allow-Origin`, telling browsers that cross-origin `fetch`/`XHR` calls from that arbitrary attacker-registered domain are permitted to read the gateway's JSON-RPC responses.

### Impact Explanation
This is a concrete allowlist bypass on the gateway's internet-facing HTTP entrypoint, matching the "allowlist ... bypass" acceptance criterion. Any operator who configures a wildcard `CORSAllowedOrigins` entry (a documented, supported pattern) unintentionally grants browser read-access to any origin whose hostname happens to share that suffix, not just genuine subdomains. This can be exploited by an unprivileged external attacker who simply registers a domain ending in the target suffix (e.g. `notexample.com` when `*.example.com` is allowlisted) and lures a victim's browser to it, enabling cross-origin reads of gateway responses that were intended to be restricted to the operator's own subdomains.

### Likelihood Explanation
Exploitation only requires: (1) an operator using the documented wildcard CORS feature (`CORSAllowedOrigins`), and (2) an attacker registering an inexpensive domain with the matching suffix. No privileged access or code changes are required, and the flawed logic is always active whenever `CORSEnabled` is true and any wildcard entry is configured.

### Recommendation
Fix `isAllowedOrigin` to require a `.` boundary before the suffix (i.e., match only when `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)`), mirroring correct wildcard certificate matching semantics (single-label match only, with an explicit dot separator) rather than a raw string suffix comparison.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.example.com"]`.
2. From a browser page hosted at `https://notexample.com`, issue a `fetch("https://gateway-host/path", {mode: "cors"})` request with `Origin: https://notexample.com`.
3. `isAllowedOrigin` computes `allowedHost = "example.com"` and evaluates `strings.HasSuffix("notexample.com", "example.com")`, which is `true`.
4. The gateway responds with `Access-Control-Allow-Origin: https://notexample.com`, allowing the browser to read the response cross-origin, despite `notexample.com` not being an intended subdomain of `example.com`. [3](#0-2)

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
