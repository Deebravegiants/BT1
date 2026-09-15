The strongest analog to CVE-2017-18190's hostname-whitelist bypass in this codebase is the CORS wildcard-origin check in the gateway's internet-facing HTTP server.

## Analysis

`core/services/gateway/network/httpserver.go`'s `isAllowedOrigin` implements the wildcard match for entries like `*.remix.com` by stripping the `*.` prefix and then doing a **plain string suffix check with no subdomain-boundary (`.`) verification**:

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [1](#0-0) 

Just like CUPS's `valid_host()` trusted any hostname ending in `.localdomain` without confirming it actually resolved to loopback, this code trusts any origin string that merely ends with the configured suffix, without confirming a `.` precedes it. An attacker who registers (or already owns) a domain such as `notremix.com` will satisfy `strings.HasSuffix("notremix.com", "remix.com")` even though it is not a subdomain of `remix.com` at all — it's a completely separate, attacker-controlled name that happens to share a trailing character sequence.

This check gates the reflected CORS response in `handleRequest`:
```go
if s.config.CORSEnabled {
    origin := r.Header.Get("Origin")
    if s.isAllowedOrigin(origin) {
        w.Header().Set("Access-Control-Allow-Origin", origin)
        ...
``` [2](#0-1) 

Because `CORSAllowedOrigins` and `CORSEnabled` are part of `HTTPServerConfig`, wired straight into the gateway's public-facing HTTP server used to relay JSON-RPC requests [3](#0-2) , and reachable by any unprivileged remote client sending a normal cross-origin browser request, this is directly analogous to the CVE's bug class: a naming-based allowlist entry that can be satisfied by an attacker-chosen hostname without actually being a member of the intended trust domain.

### Title
CORS wildcard-origin allowlist bypass via missing subdomain-boundary check - (File: core/services/gateway/network/httpserver.go)

### Summary
`isAllowedOrigin` in the Gateway's internet-facing HTTP server treats any wildcard entry `*.<suffix>` as matching any `Origin` header whose string simply ends with `<suffix>`, without requiring a `.` boundary. Any attacker-owned domain ending with the configured suffix (e.g. `evilremix.com` for an allowlist entry `*.remix.com`) passes the check.

### Finding Description
The wildcard-matching branch strips the `*.` prefix from the configured allowed origin and performs `strings.HasSuffix(originHost, allowedHost)` [1](#0-0) . This is a purely lexical suffix test: it does not require that the character preceding the matched suffix in `originHost` be a `.`. As a result, `originHost` values like `notremix.com`, `evilremix.com`, or `attacker-remix.com` — none of which are subdomains of `remix.com` — satisfy the suffix check and are treated as trusted origins.

### Impact Explanation
Any operator that configures a wildcard `CORSAllowedOrigins` entry (a documented, supported pattern per the code comment "check for wildcard host match (e.g., *.remix.com)") unintentionally allowlists an unbounded set of attacker-registrable domains. This weakens the origin allowlist enforced by the gateway's public HTTP server [4](#0-3) , allowing a malicious web page hosted on such a domain to have its cross-origin requests reflected with `Access-Control-Allow-Origin`, undermining the intended allowlist boundary for the gateway's message-relay API.

### Likelihood Explanation
Exploitation requires only that the operator use a wildcard entry (a normal, supported configuration) and that the attacker register/control any domain sharing the suffix string — no privileged access, no DNS rebinding infrastructure, and no interaction with node internals is needed, making this readily reachable by any unprivileged remote actor.

### Recommendation
Fix the wildcard match to require a proper subdomain boundary, e.g. check that `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)`, rather than a raw string-suffix comparison.

### Proof of Concept
1. Configure gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. Attacker registers `https://evilremix.com` (or any domain ending in `remix.com` without a preceding dot) and hosts a page there that issues a `fetch()` to the gateway endpoint with `Origin: https://evilremix.com`.
3. `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilremix.com", "remix.com")` is true, and the gateway responds with `Access-Control-Allow-Origin: https://evilremix.com`, satisfying CORS for the attacker's origin.

### Citations

**File:** core/services/gateway/network/httpserver.go (L40-55)
```go
type HTTPServerConfig struct {
	Host                   string
	Port                   uint16
	TLSEnabled             bool
	TLSCertPath            string
	TLSKeyPath             string
	Path                   string
	ContentTypeHeader      string
	ReadTimeoutMillis      uint32
	WriteTimeoutMillis     uint32
	RequestTimeoutMillis   uint32
	MaxRequestBytes        int64
	MaxRequestBytesLimiter limits.BoundLimiter[config.Size] // supersedes MaxRequestBytes, if set
	CORSEnabled            bool
	CORSAllowedOrigins     []string
}
```

**File:** core/services/gateway/network/httpserver.go (L184-190)
```go
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
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
