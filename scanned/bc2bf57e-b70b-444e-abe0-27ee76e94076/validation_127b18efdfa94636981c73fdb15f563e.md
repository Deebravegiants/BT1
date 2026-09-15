Confirmed: the wildcard CORS-origin matcher in the gateway's internet-facing HTTP server has an "unbounded suffix" flaw that is the same bug class as the Ranger `*`-wildcard CVE — it treats `*.` as "any string that has this text as a suffix" instead of "any subdomain of this domain," so it fails to require a `.` boundary.

### Title
CORS wildcard-origin matcher allows subdomain-boundary bypass leading to allowlist bypass - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's user-facing HTTP server (`core/services/gateway/network/httpserver.go`) supports wildcard entries like `https://*.example.com` in `CORSAllowedOrigins`. The matching logic in `isAllowedOrigin` strips the `*.` prefix and then does a raw `strings.HasSuffix` check against the browser-supplied `Origin` header, without validating that a `.` (label) boundary exists between the attacker-controlled prefix and the allowed domain suffix.

### Finding Description [1](#0-0) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
For an allowlist entry `*.remix.com`, `allowedHost` becomes `remix.com`, and any `originHost` that merely *ends with* the literal bytes `remix.com` — such as `evilremix.com` or `not-remix.com` — passes `strings.HasSuffix`, even though it is not a subdomain of `remix.com`. This is structurally the same defect class as CVE-2017-7676 (Apache Ranger): a wildcard-style matcher is applied without properly delimiting what is matched to the intended token boundary, causing characters adjacent to the match to be effectively ignored/misinterpreted, so attacker-chosen strings satisfy a pattern they should not.

This function is invoked directly from `handleRequest` for every incoming request to the Gateway's user-facing HTTP endpoint whenever CORS is enabled: [2](#0-1) 

If `isAllowedOrigin` returns true, the server reflects the attacker-controlled `Origin` header verbatim into `Access-Control-Allow-Origin`.

### Impact Explanation
An unprivileged attacker who registers or controls a domain that merely ends with the same characters as an allowed suffix (e.g. `evilremix.com` when `*.remix.com` is allowlisted) can get their origin reflected in `Access-Control-Allow-Origin`. This lets a page hosted on the attacker's domain make cross-origin browser requests to the Gateway's user-facing JSON-RPC endpoint and read the responses, which is the exact CORS allowlist-bypass class called out in the "Validate" rules (allowlist bypass reachable from an unprivileged client). Depending on what tokens or session state a victim's browser holds and attaches to such requests (e.g., a bearer token stored client-side and sent by application JS), this can enable cross-user response confusion / unauthorized use of the victim's credentials against the Gateway API.

### Likelihood Explanation
Exploitability depends on an operator configuring a wildcard CORS entry (`*.<domain>`) for the Gateway `UserServerConfig.CORSAllowedOrigins`, which is a documented, supported feature (see tests in `core/services/gateway/network/httpserver_test.go` exercising `https://*.ethereum.org` etc.). Any operator using this common convenience pattern is exposed; the attacker only needs to register/control a domain sharing the suffix bytes, no privileged access is required, and the check runs on every unauthenticated CORS preflight/request.

### Recommendation
Require a `.` immediately before the matched suffix (or an exact-length-boundary check) so that only true subdomains match, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".remix.com"
    if strings.HasSuffix(originHost, suffix) || originHost == suffix[1:] {
        return true
    }
}
```
or use `strings.HasSuffix(originHost, "."+allowedHost)` after stripping `*.`.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. As an unauthenticated client, send a request/preflight to the Gateway user endpoint with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`, even though `evilremix.com` is not a subdomain of `remix.com`, confirming the allowlist bypass. [3](#0-2)

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
