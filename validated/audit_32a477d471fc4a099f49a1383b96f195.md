### Title
CORS Allowlist Bypass via Unanchored Suffix Match in Gateway HTTP Server Wildcard Origin Check - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's HTTP server (an internet-facing component that accepts unauthenticated user requests) validates the `Origin` header against an operator-configured `CORSAllowedOrigins` allowlist using `isAllowedOrigin`. When a wildcard entry like `*.example.com` is configured, the code strips the `*.` prefix and then uses `strings.HasSuffix(originHost, allowedHost)` to decide if a request origin matches. This check is not boundary-anchored: it treats any origin string that merely *ends with* the allowed substring as a match, even when there is no subdomain separator (`.`) present. An attacker-controlled origin such as `evilexample.com` would satisfy `HasSuffix("evilexample.com", "example.com")` and be incorrectly treated as an allowed subdomain of `example.com`, bypassing the allowlist intended to restrict cross-origin access to the gateway.

### Finding Description
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements origin matching for CORS: [1](#0-0) 

Specifically, the wildcard-matching branch:

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

This mirrors the exact bug class described in the external report: an allowlist check that inspects only a substring/prefix of the input (here, a trailing substring match on the host) without validating token/label boundaries, letting an attacker construct an input that satisfies the raw string match while not conforming to the intended semantic (a true subdomain relationship). In the mcp-shell case, `parts[0] == "/bin/bash"` matched the allowlist while ignoring the `-c` argument that changed the actual behavior; here, `HasSuffix(originHost, allowedHost)` matches while ignoring whether the preceding character is a `.` — the boundary that distinguishes a legitimate subdomain (`app.example.com`) from an attacker-registered look-alike domain (`evilexample.com`, `notexample.com`, `xexample.com`).

Because `CORSAllowedOrigins` and `CORSEnabled` are the config knobs that drive this logic, and the server is reachable by any unauthenticated client (it is the JSON-RPC/HTTP surface fronting the gateway's handlers, e.g., vault, workflow, capabilities handlers), a browser-based attacker who registers a look-alike domain (e.g. `evil-chain.link` or `notchain.link` when the operator's wildcard is `*.chain.link`) can craft cross-origin requests from that domain that the gateway will treat as an allowed origin.

### Impact Explanation
If an operator relies on the `*.` wildcard form in `CORSAllowedOrigins` to scope which web front-ends may talk to the gateway cross-origin, this bug allows any attacker who controls a domain sharing the same trailing character sequence (no dot boundary required) to be treated as an allowed origin. Combined with credentialed CORS requests, this can let a malicious website issue authenticated cross-origin requests against the gateway on behalf of a victim's browser session, resulting in cross-user response confusion / request forgery against gateway handlers (vault secrets, workflow triggers, capability targets) — consistent with the rules' criteria of "cross-user response confusion" and "allowlist bypass" via an internet-facing gateway.

### Likelihood Explanation
The bypass requires no authentication and no special privileges — only that (a) the operator has configured a wildcard entry in `CORSAllowedOrigins` (a documented, supported configuration pattern per the `*.remix.com` example in the comment), and (b) the attacker can register or control a domain name ending in the allowed suffix without a preceding dot. Domain registration constraints make some suffixes harder to abuse (e.g., abusing `.com` directly requires controlling a domain literally ending in `example.com` as one word), but for shorter or generic allowed suffixes this is trivially achievable, and it is a pure logic bug independent of network position — it is exploitable by any unprivileged external client sending crafted `Origin` headers.

### Recommendation
Anchor the suffix match to a label boundary. Replace:
```go
if strings.HasSuffix(originHost, allowedHost) {
    return true
}
```
with a check that requires the origin host to equal the allowed host or be `"."+allowedHost` suffixed, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
This mirrors the CVE's own remediation guidance (validate the full logical unit, not just a raw prefix/suffix match) and eliminates the possibility of unrelated domains satisfying the allowlist.

### Proof of Concept
1. Operator configures the gateway with `CORSAllowedOrigins = ["*.example.com"]` and `CORSEnabled = true` (see config fields in `core/services/gateway/network/httpserver.go:53-54`).
2. An attacker registers/controls `evilexample.com` and serves a webpage there.
3. A victim's browser, visiting `evilexample.com`, sends an XHR/fetch request to the gateway's HTTP endpoint with `Origin: https://evilexample.com`.
4. `isAllowedOrigin` splits the origin, computes `originHost = "evilexample.com"`, strips the wildcard prefix to get `allowedHost = "example.com"`, and evaluates `strings.HasSuffix("evilexample.com", "example.com")`, which is `true`.
5. The gateway treats `evilexample.com` as an allowed CORS origin, even though it is not a subdomain of `example.com`, allowing the attacker's page to make (potentially credentialed) cross-origin requests against the gateway that the allowlist was intended to block.

Note: I was not able to trace, within the available tool budget, the exact code path where `isAllowedOrigin`'s return value is applied to `Access-Control-Allow-Origin`/credential headers (that logic likely lives in `handleRequest`, whose full body I did not fully retrieve). The root-cause matching defect itself is confirmed directly from the source shown above; the precise blast radius (whether credentials are echoed) would benefit from further review of `handleRequest` in the same file.

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
