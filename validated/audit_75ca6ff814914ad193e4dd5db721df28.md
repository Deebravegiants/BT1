Confirmed root cause: the wildcard CORS host check in `isAllowedOrigin` at `core/services/gateway/network/httpserver.go:184-190` strips the `*.` prefix from a configured allowed host and then only checks `strings.HasSuffix(originHost, allowedHost)`, without requiring a `.` boundary between the attacker-controlled label and the allowed suffix. This is the same bug class as the goshs advisory (a boundary-unaware string containment check substituting for a real hierarchical/path boundary check) — here applied to a hostname/CORS "jail" instead of a filesystem path.

### Title
CORS wildcard-origin bypass via boundary-unaware suffix match in gateway HTTP server allows any domain sharing a suffix to be treated as an allowed origin - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's public HTTP server (`core/services/gateway/network/httpserver.go`) supports configuring CORS allowed origins including wildcard subdomain entries such as `https://*.remix.ethereum.org`. The wildcard-matching logic in `isAllowedOrigin` strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` [1](#0-0)  with no verification that the matched suffix is preceded by a `.` (subdomain) separator. Any attacker-registered domain whose name happens to end with the configured suffix — not just a genuine subdomain — is accepted as an allowed origin.

### Finding Description
`isAllowedOrigin` compares the incoming `Origin` header host against each configured `CORSAllowedOrigins` entry [2](#0-1) . For wildcard entries it does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
This treats `*.remix.ethereum.org` as equivalent to "any hostname string ending in `remix.ethereum.org`", rather than "any hostname that is a proper subdomain of `remix.ethereum.org`". Because there is no check that a `.` immediately precedes the matched suffix, a domain like `evilremix.ethereum.org` — or more maliciously, an attacker-purchased domain like `notremix.ethereum.org` or even `attackerremix.ethereum.org` — passes the check even though it is not a subdomain of the intended origin at all; any domain string that happens to end with the same characters satisfies `strings.HasSuffix`. This is the identical bug class as the goshs SFTP root escape: a raw string prefix/suffix comparison used in place of a real hierarchical boundary check (`root + separator` vs. bare prefix in goshs; `"." + allowedHost` vs. bare suffix here).

`handleRequest` then reflects the attacker's `Origin` verbatim into `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true [3](#0-2) , granting the attacker-controlled origin the same CORS response-reading rights as a legitimately configured subdomain.

### Impact Explanation
Any operator who configures a wildcard CORS entry (e.g., `https://*.chain.link`) to allow their own subdomains to call the gateway's JSON-RPC HTTP endpoint unintentionally also allows any domain an attacker registers that merely ends with the same label sequence (e.g., `evilchain.link`, `notchain.link`) to read cross-origin responses from the gateway via browser JavaScript. Because the gateway HTTP endpoint is the internet-facing entry point for JSON-RPC requests (vault, workflow-execute, HTTP-trigger, etc.), this allows a malicious website to bypass the intended origin allowlist and interact with/read gateway responses cross-origin, undermining the allowlist boundary that operators rely on for browser-based clients.

### Likelihood Explanation
Exploitation requires no privileges: an attacker only needs to register/control a domain string ending in the same characters as a configured wildcard suffix and lure a victim to a page on that domain, or directly script cross-origin requests from it. The wildcard suffix check is straightforward to bypass since suffix collision is easy to engineer (e.g., prefixing the legitimate label with any character sequence). This requires the operator to have configured a wildcard `CORSAllowedOrigins` entry, which is a supported and documented configuration pattern.

### Recommendation
Replace the bare suffix check with a boundary-aware comparison, requiring the origin host to equal the allowed base host or end with `"." + allowedHost` (i.e., `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`), mirroring the `root + separator` fix pattern recommended for the goshs advisory. Add regression tests for sibling/suffix-collision hostnames (e.g., `evilremix.ethereum.org` vs. `*.remix.ethereum.org`) in addition to the existing legitimate-subdomain test cases.

### Proof of Concept
Given gateway config `CORSAllowedOrigins = ["https://*.remix.ethereum.org"]`:
1. An attacker registers/controls `https://evilremix.ethereum.org` (or any domain ending in the literal characters `remix.ethereum.org`, e.g. `https://attackerremix.ethereum.org`).
2. A victim's browser visits a page hosted on that attacker domain, which issues a `fetch()`/XHR to the gateway's HTTP endpoint with `Origin: https://evilremix.ethereum.org`.
3. In `isAllowedOrigin`, `originHost = "evilremix.ethereum.org"`, `allowedHost` after stripping `*.` = `"remix.ethereum.org"`. `strings.HasSuffix("evilremix.ethereum.org", "remix.ethereum.org")` evaluates `true` [4](#0-3)  even though `evilremix.ethereum.org` is not a subdomain of `remix.ethereum.org`.
4. `handleRequest` reflects `Access-Control-Allow-Origin: https://evilremix.ethereum.org` [5](#0-4) , letting the attacker page read the gateway's JSON-RPC response cross-origin, bypassing the intended origin allowlist.

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
