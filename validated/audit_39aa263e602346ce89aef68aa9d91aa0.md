## Finding [1](#0-0) 

### Title
CORS Allowed-Origin Wildcard Suffix Comparison Omits the Subdomain Separator - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's HTTP server validates cross-origin requests against an operator-configured allowlist (`CORSAllowedOrigins`). For wildcard entries such as `*.example.com`, the check strips the `*.` prefix and then tests `strings.HasSuffix(originHost, allowedHost)` without ensuring a `.` (or exact host) boundary precedes the match, mirroring the CVE-2026-77814 bug class where a prefix/suffix check is missing the delimiter that would otherwise enforce the intended boundary.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  implements the wildcard branch as:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

If an operator configures `CORSAllowedOrigins` with an entry like `https://*.remix.com`, `allowedHost` becomes `remix.com`, and the code accepts any `originHost` that merely ends with the literal string `remix.com` — with no requirement that a `.` separates the attacker-controlled subdomain portion from `remix.com`. A request whose `Origin` header is `https://evilremix.com` satisfies `strings.HasSuffix("evilremix.com", "remix.com")`, so it is wrongly treated as an allowed subdomain of `remix.com`, even though `evilremix.com` is an entirely different, attacker-registrable domain. This is the exact bug class described in the report: a prefix/suffix membership check that omits the separator character needed to make the confinement/allowlist meaningful.

This check is exercised directly from `handleRequest` [2](#0-1) , which reflects the attacker-supplied `Origin` header back via `Access-Control-Allow-Origin` and sets `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers` whenever `isAllowedOrigin` returns true — reachable by any unauthenticated client sending a normal HTTP request to the Gateway's user-facing endpoint.

### Impact Explanation
If `CORSEnabled` is set with a wildcard allowlist entry (a supported, documented configuration — see `core/scripts/gateway/sample_config.toml` and `core/scripts/gateway/sample_config_tls.toml`), an attacker who registers a domain that merely ends with the allowed suffix (e.g., `evilremix.com` for allowlisted `*.remix.com`, or `notexample.com` for `*.example.com`) can host a malicious webpage that makes cross-origin requests to the Gateway and, thanks to the reflected `Access-Control-Allow-Origin` header, read authenticated/credentialed responses from victim browsers. This is a cross-user response confusion / allowlist bypass affecting the internet-facing Gateway HTTP server.

### Likelihood Explanation
Exploitability depends on: (1) the operator enabling CORS and configuring at least one wildcard origin (a supported feature, not a misconfiguration outside intended usage), and (2) an attacker being able to register or control a domain name that has the allowed suffix as a trailing substring without a preceding dot. Domain names of this shape (e.g., `evilexample.com` vs `*.example.com`) are trivially registrable by any external attacker, so likelihood is driven mainly by whether wildcard CORS entries are used in deployments — which the presence of dedicated sample configs suggests is an anticipated, real usage pattern.

### Recommendation
Fix the suffix comparison so the wildcard match requires a `.` boundary (or exact match), e.g.:
```go
if strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost {
    return true
}
```
This mirrors the referenced fix pattern of joining with the separator (`os.sep` there, `.` here) before the containment check.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. From an attacker-controlled page hosted at `https://evilremix.com`, issue a `fetch`/XHR request to the Gateway endpoint with `Origin: https://evilremix.com`.
3. The server's `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilremix.com", "remix.com")` is true, so the response includes `Access-Control-Allow-Origin: https://evilremix.com`, letting the attacker's script read the response cross-origin — even though `evilremix.com` was never intended to be trusted.

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
