## Finding: CORS Origin Allowlist Bypass via Unanchored Suffix Match in Gateway HTTP Server

The Grav CMS bug class (unanchored string match on Referer/Origin causing an attacker-controlled domain to be treated as same-origin) has a direct analog in the Chainlink Gateway's CORS origin allowlist check.

### Title
CORS Origin Allowlist Bypass via Unanchored Suffix Match on Wildcard Domains - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway HTTP server's wildcard-domain CORS check uses `strings.HasSuffix(originHost, allowedHost)` after stripping the `*.` prefix from a configured allowed origin, with no check that the matched suffix is preceded by a `.` (domain label boundary). This mirrors the Grav CMS `str_starts_with($referrer, $base)` bug: an unanchored substring match is used where an anchored, delimiter-aware match is required.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  parses the request's `Origin` header and each configured allowed origin into scheme/host/port, then for wildcard entries does:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

If an operator configures `CORSAllowedOrigins = ["https://*.remix.ethereum.org"]`, then `allowedHost` becomes `remix.ethereum.org`. `strings.HasSuffix` only checks that the origin host string ends with that literal substring — it does not verify that a `.` (or start-of-string) immediately precedes the match. An attacker who registers a domain like `evilremix.ethereum.org`... more precisely any domain whose name simply concatenates to end in `remix.ethereum.org` without a dot boundary, e.g. `notremix.ethereum.org` is actually a valid subdomain, but `xremix.ethereum.org` is also a valid subdomain (still matches intended pattern). The real bypass is when the attacker's *entire registrable domain* (not a subdomain) happens to end in the same characters, e.g. an attacker-controlled domain `attackerremix.ethereum.org`-style is still a subdomain and technically fine — but critically, an attacker can also buy/control any domain whose label boundary does not align, e.g. host `evilremix.ethereum.org.attacker.tld` is blocked (suffix wouldn't match), but a domain like `xyzremix.ethereum.org` where `xyz` is glued directly onto the label without a preceding dot is only prevented if `strings.HasSuffix` is dot-aware — which it is not. Concretely: `strings.HasSuffix("attacker-remix.ethereum.org", "remix.ethereum.org")` is true and `attacker-remix.ethereum.org` is a domain fully controlled by an attacker who registers the parent zone `-remix.ethereum.org`... 

The unambiguous, unauthenticated exploit case is when the configured wildcard suffix does not start exactly at a label boundary in the attacker's domain, allowing something like allowed=`*.example.com` to match attacker-registered `notexample.com` is false (HasSuffix requires exact trailing characters "example.com", and "notexample.com" does end with "example.com" — true, and `notexample.com` is a completely independent, attacker-registrable domain, not a subdomain of `example.com` at all). This is the exact same class of bug as Grav's: **the check conflates "ends with configured suffix" with "is a subdomain of the configured domain,"** letting an attacker register any domain that textually ends with the allowed suffix.

### Impact Explanation
If exploited, an attacker-controlled origin (e.g., `evilexample.com` against an allowlist entry `*.example.com`) is treated as trusted. The server responds with `Access-Control-Allow-Origin: <attacker origin>` [3](#0-2) , allowing the attacker's web page (loaded by a victim user/browser with a valid session/credentials against the Gateway) to make cross-origin credentialed requests and read the JSON responses from the Gateway's `ProcessRequest` handler — potentially including job run results, DON responses, or other data routed through the internet-facing Gateway.

### Likelihood Explanation
Exploitability depends on the exact wildcard domain configured by the operator (e.g. `CORSAllowedOrigins`) and whether an attacker can register/control a domain that textually ends with the allowed suffix without being an actual subdomain. This is registrable in DNS by any external, unauthenticated attacker (domain registration), making the precondition attacker-controlled and independent of any node privilege.

### Recommendation
Change the wildcard match to require a `.` boundary immediately before the suffix (or exact equality to the allowed domain), e.g.:
```go
if strings.HasSuffix(originHost, allowedHost) &&
   (originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)) {
    return true
}
```
This ensures `originHost` is either exactly `allowedHost` or a genuine subdomain (`*.allowedHost`), closing the unanchored-suffix bypass, analogous to how Grav's fix would require a `/`- or end-of-string-anchored match after the base origin.

### Proof of Concept
1. Configure the Gateway with `CORSAllowedOrigins = ["https://*.trusted.com"]`.
2. Attacker registers/controls `https://eviltrusted.com` (note: NOT a subdomain of `trusted.com`).
3. Attacker's page sends a cross-origin request to the Gateway with header `Origin: https://eviltrusted.com`.
4. `isAllowedOrigin` computes `allowedHost = "trusted.com"`, `originHost = "eviltrusted.com"`, and `strings.HasSuffix("eviltrusted.com", "trusted.com")` returns `true`.
5. The Gateway responds with `Access-Control-Allow-Origin: https://eviltrusted.com`, and the attacker's page can now read cross-origin, credentialed Gateway responses via `fetch()`/XHR from the victim's browser. [4](#0-3)

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-202)
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

func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}
```
