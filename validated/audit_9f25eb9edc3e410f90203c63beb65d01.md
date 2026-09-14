### Title
Gateway CORS wildcard allowlist uses unanchored suffix matching, letting attacker-registered domains impersonate trusted origins - ([File: core/services/gateway/network/httpserver.go])

### Summary
The gateway's user-facing HTTP server validates `Origin` headers against `CORSAllowedOrigins` wildcard entries (e.g. `*.example.com`) using an unanchored `strings.HasSuffix` check instead of verifying a proper subdomain boundary (a leading `.` or exact match). An attacker who registers a domain that merely *ends with* the configured suffix (e.g. `evilexample.com` for an allowlist entry `*.example.com`) is treated as a trusted origin, exactly mirroring the "allowlist uses suffix matching" root cause described in the reference advisory (bearer token/response leaked to a suffix-allowlisted but untrusted host).

### Finding Description
`isAllowedOrigin` in [1](#0-0)  implements wildcard host matching as follows: for an allowlist entry starting with `*.`, it strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)`. This is not anchored to a domain-label boundary. Given `allowedHost = "example.com"`, the check `strings.HasSuffix("evilexample.com", "example.com")` returns `true`, even though `evilexample.com` is a distinct, attacker-controlled domain and not a subdomain of `example.com`.

This function is invoked from `handleRequest` at [2](#0-1) , where, if the check passes, the gateway echoes the attacker's `Origin` value back in `Access-Control-Allow-Origin`, along with `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`, for every request hitting the user-facing gateway endpoint. The gateway's `handleRequest` also extracts a bearer/JWT token from the `Authorization` header on every request ( [3](#0-2) ) and forwards the raw response body from `ProcessRequest` to the browser with the (incorrectly granted) CORS headers attached.

This is directly analogous to the reported bug class: an allowlist relying on naive suffix matching (rather than a properly delimited subdomain check) can be satisfied by an unrelated, attacker-registered domain, causing sensitive material (in the OpenClaw case, a bearer token; here, the gateway's JSON-RPC response body/CORS-exposed content) to be exposed to a host the operator never intended to trust.

### Impact Explanation
If an operator configures `CORSAllowedOrigins` with any wildcard entry (a documented, supported feature — see `sample_config.toml` allowing `CORSAllowedOrigins` and the wildcard-specific test cases in `httpserver_test.go`), an unprivileged external attacker can register a domain sharing the same suffix (no dot required) and have pages hosted there treated as an allowed CORS origin by the gateway. This lets attacker-controlled JavaScript running in a victim's browser make cross-origin requests to the gateway and read the JSON-RPC responses (which can include job/workflow results, or other data returned through the gateway's HTTP capability), because the browser will honor the spoofed `Access-Control-Allow-Origin` reflection. This is a concrete allowlist-bypass leading to cross-user/cross-origin response disclosure — the CWE-201/CWE-346-class issue matching the report's underlying "suffix-based allowlist trusts the wrong host" defect.

### Likelihood Explanation
Exploitability depends on an operator enabling CORS with a wildcard allowlist entry — this is an explicitly supported and tested configuration path (not a hypothetical), as shown by the wildcard test cases in `httpserver_test.go`. Registering a domain that satisfies an unanchored suffix match (e.g., buying `evil<allowed-domain>` when the allowlist is `*.<allowed-domain>`) requires no privileges beyond registering a domain name, making this reachable by any unprivileged actor able to lure a victim to a page they control.

### Recommendation
Anchor the wildcard match on a domain-label boundary instead of a raw suffix check, e.g. require that `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)`, ensuring `evilexample.com` cannot match `*.example.com`.

### Proof of Concept
1. Gateway operator configures: `CORSEnabled = true`, `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Attacker registers `https://evilexample.com` and hosts a page there with JS that sends `fetch("https://gateway-host/user", {headers: {Origin: "https://evilexample.com", ...}})` (or simply loads the page in a browser, which sets `Origin` automatically).
3. In `isAllowedOrigin` ( [4](#0-3) ), `allowedHost` becomes `"example.com"` after stripping `*.`, and `strings.HasSuffix("evilexample.com", "example.com")` evaluates `true`.
4. The gateway responds with `Access-Control-Allow-Origin: https://evilexample.com`, allowing the attacker's page to read the JSON-RPC response returned by `ProcessRequest`.

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

**File:** core/services/gateway/network/httpserver.go (L226-231)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}
```
