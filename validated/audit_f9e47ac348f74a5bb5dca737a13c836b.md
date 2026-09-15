### Title
CORS wildcard-origin allowlist bypass via missing domain-boundary check in `isAllowedOrigin` - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's HTTP server validates cross-origin requests against an admin-configured `CORSAllowedOrigins` list. For wildcard entries (e.g. `*.remix.com`), the check strips the `*.` prefix and then uses `strings.HasSuffix(originHost, allowedHost)` with no domain-boundary (dot) check, exactly the same missing-boundary bug class described in the File Browser advisory (`strings.HasPrefix` without a trailing separator). Here the equivalent flaw is a suffix match without a leading separator, so any attacker-controlled hostname that merely ends with the configured domain string is treated as allowed.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  parses the request `Origin` header and each configured allowed origin, then performs:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

If an operator configures `*.remix.com` intending to allow any subdomain of `remix.com`, `allowedHost` becomes `"remix.com"`. The check then accepts *any* hostname ending in that literal string, with no requirement that the character immediately preceding the match be a `.` (domain boundary). An attacker who registers `evilremix.com` (or `attacker-remix.com`) satisfies `strings.HasSuffix("evilremix.com", "remix.com") == true`, so their origin is treated as an allowed subdomain even though it is a completely unrelated domain that merely shares a suffix.

This mirrors the reported File Browser bug class precisely: a prefix/suffix string check used for access-control decisions without enforcing a path/domain-boundary separator, allowing sibling/adjacent names to be conflated with the intended scope.

### Impact Explanation
When `isAllowedOrigin` returns true, `handleRequest` reflects the attacker's `Origin` back in `Access-Control-Allow-Origin` and permits the browser to complete cross-origin requests to the Gateway [2](#0-1) . This lets a page hosted on an attacker-controlled domain that merely shares a suffix with the operator's trusted domain (e.g. `evilremix.com` vs. the intended `*.remix.com`) issue browser-originated requests to the Gateway's HTTP API as if it were a trusted origin, bypassing the operator's intended CORS allowlist restriction. Depending on how the Gateway API is used by downstream handlers, this can enable request forgery or unauthorized interaction from an unprivileged, external, browser-based attacker.

### Likelihood Explanation
Exploitability only requires the operator to configure any wildcard CORS entry (a documented, supported feature) and the attacker to register or control a domain with the matching suffix — no privileged access or insider position is needed, and the check is reachable directly from any web client sending requests to the internet-facing Gateway HTTP endpoint.

### Recommendation
Enforce a domain boundary when doing the wildcard suffix match, e.g.:

```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // keep the leading dot: ".remix.com"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```

This ensures `evilremix.com` no longer matches `*.remix.com`, while `foo.remix.com` still does.

### Proof of Concept
1. Operator configures Gateway with `CORSAllowedOrigins: ["https://*.remix.com"]`.
2. Attacker hosts a page at `https://evilremix.com` and, from a victim's browser, sends a fetch/XHR request to the Gateway's HTTP endpoint with `Origin: https://evilremix.com`.
3. `isAllowedOrigin` computes `allowedHost = "remix.com"` and evaluates `strings.HasSuffix("evilremix.com", "remix.com")`, which is `true`.
4. The Gateway responds with `Access-Control-Allow-Origin: https://evilremix.com`, allowing the attacker's page to read the cross-origin response despite not being a subdomain of `remix.com`.

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
