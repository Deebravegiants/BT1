### Title
CORS wildcard-origin allowlist bypass via unbounded suffix match - ([File: core/services/gateway/network/httpserver.go])

### Summary
The gateway's HTTP server validates the `Origin` header against a configured wildcard allowlist using `strings.HasSuffix` without any domain-boundary (dot) check, allowing an attacker-registered domain that merely ends with the allowed suffix (not a true subdomain) to be treated as trusted and receive `Access-Control-Allow-Origin` reflection.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  handles wildcard entries (e.g. `*.remix.com`) by stripping the `*.` prefix and then checking `strings.HasSuffix(originHost, allowedHost)`:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

This is the same class of bug as CVE-2026-14336: a "suffix trick" check that lacks a boundary character (`.`) between the matched suffix and the rest of the string. For an allowlist entry `*.remix.com`, the code strips to `remix.com` and then accepts any origin host string ending in `remix.com` — including `evilremix.com`, `notremix.com`, or `attacker-remix.com` — none of which are actual subdomains of `remix.com`. There is no check that the character preceding the matched suffix is a `.`.

The result is fed directly into `handleRequest`, which reflects the attacker-controlled `Origin` value back with credential-enabling CORS headers:
```go
if s.isAllowedOrigin(origin) {
    w.Header().Set("Access-Control-Allow-Origin", origin)
    w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}
``` [3](#0-2) 

This is reachable by any unauthenticated/unprivileged browser client sending requests to the gateway's internet-facing HTTP endpoint, matching the "allowlist bypass" and "internet-facing gateway" scope in this scan.

### Impact Explanation
An attacker who registers a domain merely ending with an operator's configured wildcard suffix (e.g. `evilremix.com` when `*.remix.com` is allowlisted) can host a malicious webpage that is treated by the gateway as an allowed CORS origin. Browsers from victims visiting the attacker's page can then make cross-origin, credentialed requests to the gateway and read responses that should be restricted to trusted origins — a cross-origin allowlist bypass enabling data exfiltration or gateway API abuse under an impersonated trusted origin.

### Likelihood Explanation
Exploitability depends on the CORS allowlist actually containing a wildcard entry (`*.domain.com`) in the operator's `CORSAllowedOrigins` config [4](#0-3) , which is a documented/sample configuration option [5](#0-4) . Any operator using wildcard CORS entries (a common convenience pattern) is exposed, and the attack requires only registering a lookalike domain and getting a victim to browse it — no privileged access needed.

### Recommendation
Fix the suffix check to require a domain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".remix.com"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
This ensures `originHost` must either equal the base domain or end with `.` + the base domain, preventing sibling/lookalike domains like `evilremix.com` from matching `*.remix.com`.

### Proof of Concept
1. Gateway operator configures `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. Attacker registers `evilremix.com` and serves a page with JS issuing a `fetch()`/`XHR` to the gateway HTTP endpoint with `Origin: https://evilremix.com`.
3. In `isAllowedOrigin`, `originHost = "evilremix.com"`, `allowedHost` becomes `"remix.com"` after stripping `*.`, and `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`.
4. The gateway responds with `Access-Control-Allow-Origin: https://evilremix.com`, allowing the attacker's page to read cross-origin responses from the gateway that were intended only for `*.remix.com` subdomains.

### Citations

**File:** core/services/gateway/network/httpserver.go (L53-54)
```go
	CORSEnabled            bool
	CORSAllowedOrigins     []string
```

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

**File:** core/services/gateway/network/httpserver.go (L196-202)
```go
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}
```

**File:** core/scripts/gateway/sample_config.toml (L1-1)
```text
[UserServerConfig]
```
