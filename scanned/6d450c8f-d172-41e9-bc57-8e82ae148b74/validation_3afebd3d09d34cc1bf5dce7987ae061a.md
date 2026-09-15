Confirmed: this is a genuine analog of the CVE-2014-2532 bug class (substring located before a wildcard bypasses an intended access restriction).

### Title
CORS wildcard-origin allowlist bypass via missing subdomain boundary check - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Gateway's internet-facing HTTP server implements a custom CORS origin check that supports wildcard entries like `*.example.com` in `CORSAllowedOrigins`. The wildcard match strips the `*.` prefix and then performs a plain suffix comparison without verifying a `.` (subdomain) boundary, so any origin host that merely ends with the configured suffix — not just true subdomains — is treated as allowed.

### Finding Description
`isAllowedOrigin` handles the wildcard case as: [1](#0-0) 
`allowedHost[2:]` strips only the two characters `"*."`, leaving the bare domain (`"example.com"`, without a leading dot). The subsequent `strings.HasSuffix(originHost, allowedHost)` then matches on raw string suffix, not on a hostname/label boundary. Consequently, an attacker-controlled origin such as `evilexample.com` or `attacker-example.com` satisfies `HasSuffix("evilexample.com", "example.com")` and is granted the same trust as a legitimate `sub.example.com`, even though it is not a subdomain of the intended domain at all. This is the same bug class as CVE-2014-2532: a substring located immediately before/around the wildcard boundary is not properly delimited, so text that merely shares a suffix bypasses the intended pattern-matching restriction.

### Impact Explanation
This check gates `Access-Control-Allow-Origin` reflection in `handleRequest`: [2](#0-1) 
The Gateway HTTP server is the internet-facing entry point for `ProcessRequest`, which is called with the raw, unauthenticated request and any `Authorization: Bearer` token. If an operator configures a wildcard entry (e.g. `*.mycompany.com`) intending to trust only genuine subdomains, an attacker who registers or controls a domain like `evilmycompany.com` can have their site's cross-origin requests to the Gateway accepted with CORS headers reflecting their Origin, enabling browser-based credentialed cross-origin requests from an unintended domain against the Gateway API from a victim's browser.

### Likelihood Explanation
Exploitation only requires the target operator to have configured any wildcard entry in `CORSAllowedOrigins` (a documented, supported feature) and requires no privileged access — an unprivileged remote attacker simply needs to register a domain sharing the same suffix and lure a victim to browse it while the CORS-protected origin check silently passes. This is a low-complexity, unprivileged-actor bug reachable directly from the internet-facing Gateway HTTP path.

### Recommendation
Fix the suffix comparison to enforce a proper subdomain boundary, e.g. require the character immediately preceding the matched suffix to be `.`, or reconstruct the comparison as `strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost` after stripping `*.`. Alternatively, split `originHost` on `.` and compare the trailing labels exactly against the labels of `allowedHost`, and add a regression test asserting that `evilexample.com` does NOT match `*.example.com`.

### Proof of Concept
Configure `CORSAllowedOrigins: ["https://*.example.com"]`. Send a preflight/actual request to the Gateway with header `Origin: https://evilexample.com`. `isAllowedOrigin` strips `"*."` from `"example.com"` (unchanged) and evaluates `strings.HasSuffix("evilexample.com", "example.com")`, which is `true`, so `handleRequest` sets `Access-Control-Allow-Origin: https://evilexample.com`, incorrectly granting CORS trust to a domain that is not a subdomain of `example.com`.

### Citations

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
