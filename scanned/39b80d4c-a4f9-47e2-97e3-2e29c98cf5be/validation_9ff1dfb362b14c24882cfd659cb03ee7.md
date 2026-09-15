### Title
Sibling-Domain CORS Origin Bypass via Boundary-less Suffix Match - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's HTTP server validates CORS `Origin` headers against a configured allowlist. For wildcard entries (e.g. `*.remix.com`), the check strips the `*.` prefix and then uses `strings.HasSuffix(originHost, allowedHost)` to decide if the origin is allowed. This is the same bug class as CVE-2026-32726: a boundary-less string comparison (there, a path prefix check; here, a hostname suffix check) that allows an attacker-controlled value that merely shares a suffix/prefix with the authorized value to pass validation, even though it is not actually a sub-resource (subdomain) of the authorized entity.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  loops over configured `CORSAllowedOrigins`, and for wildcard host entries strips the `*.` prefix and performs:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

`strings.HasSuffix` has no notion of a domain-label boundary (a `.` separator). If the operator configures `CORSAllowedOrigins = ["https://*.remix.com"]`, intending to allow only subdomains of `remix.com`, an origin such as `https://evilremix.com` or `https://notremix.com` will also satisfy `strings.HasSuffix("evilremix.com", "remix.com")`, because the suffix check does not require the preceding character to be a dot. This is structurally identical to the SciTokens bug: a prefix/suffix check without segment-boundary enforcement lets an attacker-controlled sibling value (a different-but-similarly-named host) be treated as authorized.

The scheme and port are validated exactly (`originScheme != allowedScheme`, `originPort != allowedPort` at lines 173–178), and exact host match is a strict `==` (line 181), so the vulnerability is isolated to the wildcard-suffix branch.

### Impact Explanation
`isAllowedOrigin` result is used directly in `handleRequest` to decide whether to reflect the request's `Origin` header back in `Access-Control-Allow-Origin` [3](#0-2) . This is the internet-facing Gateway HTTP endpoint that receives the JWT/auth-bearing capability requests processed by `s.handler.ProcessRequest` [4](#0-3) . If a browser-based client from an attacker-registered domain that happens to share a suffix with the legitimate allowed wildcard domain (e.g., registering `evil-remix.com` when the allowlist is `*.remix.com`, or any domain ending in the allowed suffix) makes a cross-origin request, the Gateway will set CORS headers permitting that origin to read authenticated responses via the browser, enabling cross-user response confusion / unauthorized read access to Gateway responses that were only meant for the legitimate subdomain's origin. This can lead to leakage of gateway responses (which may embed capability results, node responses, or user-specific data) to an unauthorized origin.

### Likelihood Explanation
Exploitability requires only that: (1) the operator has configured a wildcard CORS entry (a common convenience pattern, e.g. `*.remix.com`), and (2) an attacker registers or controls a domain sharing the same suffix (`evilremix.com`, `attacker-remix.com`, etc.) and lures a victim's browser to it. No privileged access or credentials are needed by the attacker — this is exploitable by any unprivileged external actor via a standard browser cross-origin request, matching the CVSS profile of the reference CVE (network vector, low complexity, no privileges, user-interaction not required for the server-side check itself).

### Recommendation
Replace the boundary-less `strings.HasSuffix` check with a boundary-aware comparison, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
This mirrors the SciTokens fix pattern of requiring a path/label separator immediately before the matched suffix, ensuring only genuine subdomains of the allowed host are matched, not sibling domains that merely share a trailing substring.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. From a browser hosted at `https://evilremix.com` (or any domain the attacker controls that ends in `remix.com` without a leading dot, e.g. `https://notremix.com`), send a cross-origin request to the Gateway HTTP endpoint with header `Origin: https://evilremix.com`.
3. `isAllowedOrigin` computes `allowedHost = "remix.com"` and `originHost = "evilremix.com"`; `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`, so the function returns `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilremix.com`, allowing the attacker's page to read the JSON response from the Gateway via JavaScript `fetch`, despite `evilremix.com` never being an authorized subdomain of `remix.com`.

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

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```
