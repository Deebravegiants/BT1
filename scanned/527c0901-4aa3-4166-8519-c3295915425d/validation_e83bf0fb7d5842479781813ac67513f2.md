### Title
CORS wildcard-origin allowlist uses unanchored suffix matching, letting attacker-registered domains bypass host validation - ([File: core/services/gateway/network/httpserver.go])

### Summary
The gateway's CORS origin validator (`core/services/gateway/network/httpserver.go`) implements wildcard host allowlisting (`*.example.com`) with an unanchored `strings.HasSuffix` check instead of a boundary-aware subdomain match. This is the same bug class as the reported `http-proxy-middleware` advisory: attacker-controlled request metadata (the `Origin` header, which reflects the requester's actual domain) is matched against a configured allowlist entry using raw substring/suffix comparison rather than exact-or-properly-delimited matching, letting an unrelated, attacker-controlled hostname be treated as trusted.

### Finding Description
`isAllowedOrigin()` splits both the incoming `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port, then does an exact-match check, followed by a wildcard fallback: [1](#0-0) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

When `allowedHost` is configured as `*.remix.com`, the code strips the `*.` prefix and checks whether `originHost` ends with the literal string `remix.com` — with no check that the character preceding the match is a dot (`.`) or that the match starts at a label boundary. As a result, any hostname that merely ends with the substring `remix.com` satisfies the check, e.g. `evilremix.com`, `notremix.com`, or `attacker-remix.com`, none of which are actual subdomains of `remix.com`.

This mirrors the root cause described in GHSA-64mm-vxmg-q3vj: attacker-controlled request metadata (there, `Host`+path; here, `Origin`) is matched against a configured routing/trust key using substring/suffix containment instead of exact or properly delimited matching, so a crafted value that is merely a superstring of the configured key is accepted.

### Impact Explanation
This is reachable by any unauthenticated external client: `isAllowedOrigin` is invoked directly from `handleRequest()` on every gateway HTTP request when `CORSEnabled` is set, using the caller-supplied `Origin` header: [2](#0-1) 

An attacker who registers or controls a domain that merely ends with the configured allowed suffix (no subdomain relationship required) can have the gateway respond with `Access-Control-Allow-Origin: <attacker origin>`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, effectively granting that domain the same CORS trust as legitimate subdomains of the configured allowlist. This allows a malicious site to have browser JavaScript read cross-origin responses from the gateway's node-facing/user-facing HTTP endpoint that were only meant to be exposed to real `*.<allowed-domain>` origins, an origin-validation integrity bypass matching the CWE-187/CWE-20 classification of the source report.

### Likelihood Explanation
Exploitability depends on whether the deployment configures wildcard entries in `CORSAllowedOrigins`; if so, any external attacker who can register or control a domain sharing the allowed suffix as a plain substring (no dot boundary needed) can pass the check with a normal browser request — no special privileges, network position, or victim interaction beyond visiting the attacker's page is required.

### Recommendation
Replace the raw `strings.HasSuffix` check with a boundary-aware comparison, e.g. require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` after stripping the `*.` prefix, so `evilremix.com` no longer matches `*.remix.com`.

### Proof of Concept
Given gateway config with `CORSAllowedOrigins: ["https://*.remix.com"]` and `CORSEnabled: true`:

1. Send a request with header `Origin: https://evilremix.com`.
2. `splitURL` extracts `originHost = "evilremix.com"`; the allowlist entry yields `allowedHost = "remix.com"` after stripping `*.`.
3. `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`, so `isAllowedOrigin` returns `true` even though `evilremix.com` is not a subdomain of `remix.com`.
4. The gateway responds with `Access-Control-Allow-Origin: https://evilremix.com`, granting the attacker-controlled origin CORS trust intended only for genuine `*.remix.com` subdomains. [3](#0-2)

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
