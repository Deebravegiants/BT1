## Analysis

The Chrome CVE describes a **domain-spoofing UI bug**: an attacker-controlled page can be visually/structurally confused with a trusted origin. The closest analog in this codebase is a **flawed wildcard-origin matching check in the internet-facing Gateway HTTP server's CORS allowlist**, which lets an attacker-registered domain be mistaken for a trusted subdomain of an allowed origin.

### Title
CORS wildcard-origin allowlist match uses unanchored suffix comparison, allowing domain spoofing of trusted origins - (File: `core/services/gateway/network/httpserver.go`)

### Summary
`httpServer.isAllowedOrigin` implements wildcard-origin matching for the gateway's CORS allowlist (e.g. `*.remix.com`). When testing a wildcard entry it strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` with no requirement that the preceding character be a `.` (domain label boundary). An attacker who registers a domain such as `evilremix.com` will pass the suffix check against an allowlisted `*.remix.com` entry, even though `evilremix.com` is not a subdomain of `remix.com`.

### Finding Description [1](#0-0) 

The relevant logic:
- `splitURL` lower-cases and parses the URL into scheme/host/port for both the request `Origin` header and each configured allowlist entry.
- For an exact match it compares `originHost == allowedHost` (safe).
- For a wildcard entry (`*.host`), it strips the `*.` prefix, leaving just `host`, then does `strings.HasSuffix(originHost, allowedHost)` — this is a plain string suffix test, not a domain-label-aware comparison.

Because there is no check that `originHost` has a `.` immediately before the matched suffix (or that `originHost == allowedHost` after stripping the label), any attacker-controlled hostname that ends with the same character sequence as the allowed root domain is treated as a valid subdomain. For example, if the config allows `*.remix.com`, then origins such as `evilremix.com`, `notremix.com`, or `xremix.com` all satisfy `HasSuffix(originHost, "remix.com")` and are wrongly treated as trusted.

This is reachable directly by any unprivileged browser client sending a crafted `Origin` header to the internet-facing gateway HTTP endpoint in `handleRequest`: [2](#0-1)  — the server reflects the attacker's `Origin` value back in `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true, and serves the (CORS-permitted) response readable by that spoofed origin.

### Impact Explanation
A malicious website hosted on a domain crafted to satisfy the flawed suffix check (e.g. `evilremix.com` against an allowlisted `*.remix.com`) is granted the same cross-origin read access as a genuinely trusted subdomain. This is a **cross-origin/allowlist bypass via domain spoofing**: browsers on that malicious origin can perform `fetch`/XHR calls to the gateway and read JSON-RPC responses that were only intended to be exposed to explicitly trusted partner domains, undermining the security boundary the CORS allowlist is meant to enforce.

### Likelihood Explanation
Exploitation only requires an attacker to register/host a domain name that happens to end in the same character sequence as an allowlisted root domain (no wildcard dot required) and lure a victim/browser to visit it while it issues cross-origin requests to the gateway. No special privileges, node compromise, or network-layer control are needed — this is reachable from any unprivileged web client as described in the report's "domain spoofing via a crafted HTML page" pattern.

### Recommendation
Fix `isAllowedOrigin` to require a literal `.` boundary (or exact host equality) before the suffix match, e.g.:
```go
if strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost {
    return true
}
```
instead of the current unanchored `strings.HasSuffix(originHost, allowedHost)`.

### Proof of Concept
1. Configure the gateway with `CORSEnabled: true` and `CORSAllowedOrigins: ["https://*.remix.com"]`.
2. From a browser (or `curl`) send a request to the gateway HTTP path with header `Origin: https://evilremix.com`.
3. Observe the server responds with `Access-Control-Allow-Origin: https://evilremix.com`, per the reflection logic at [3](#0-2) , granting the attacker's non-subdomain origin the same cross-origin access as a legitimately allowlisted `*.remix.com` subdomain.

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
