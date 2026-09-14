## Title
CORS wildcard-origin allowlist bypass via improper suffix matching in Gateway HTTP server - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The Chainlink Gateway's HTTP server implements a custom CORS allowlist check for wildcard origins (e.g. `https://*.ethereum.org`) using a naive `strings.HasSuffix` comparison after stripping the `*.` prefix. Because the comparison does not verify that the matched suffix is preceded by a subdomain-delimiting dot, an attacker can register any domain that merely ends with the allowed suffix string (e.g. `evilethereum.org`) and have it accepted as a valid subdomain of the allowlisted origin, causing the Gateway to reflect `Access-Control-Allow-Origin` for that attacker-controlled origin.

### Finding Description
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` performs the wildcard match like this: [1](#0-0) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

For an allowlisted entry `https://*.ethereum.org`, `allowedHost` becomes `ethereum.org`. The check `strings.HasSuffix(originHost, "ethereum.org")` is `true` not only for legitimate subdomains such as `remix.ethereum.org`, but also for any origin whose hostname simply ends with the literal string `ethereum.org` without a preceding `.` — e.g. `evilethereum.org`, `notethereum.org`, or `attacker-ethereum.org`. This is the same class of bug as the CVE-2018-7160/CVE-2021-22884 report: an allowlist intended to restrict access to a specific trusted domain set is bypassed because the matching logic is too permissive (suffix/string match instead of a proper label-boundary/DNS-rebinding-safe check).

This function feeds directly into `handleRequest`, which is the entry point for all unprivileged, internet-facing client requests to the Gateway's HTTP API: [2](#0-1) 

Any external, unauthenticated caller can set an arbitrary `Origin` header (browsers do this automatically for cross-origin fetch/XHR calls; non-browser clients can set it directly), so this is fully reachable by an unprivileged actor without any credentials.

### Impact Explanation
When `isAllowedOrigin` returns a false positive, the server reflects the attacker's origin in `Access-Control-Allow-Origin` and also sets permissive `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`. If the Gateway ever pairs this with credentialed requests (cookies, or is fronted by infrastructure treating the CORS allowlist as an access-control boundary rather than defense-in-depth), a malicious website hosted at a domain crafted to satisfy the suffix (e.g., `evilethereum.org`) can make browser-originated cross-origin requests to the Gateway and read the JSON-RPC responses that would otherwise be restricted to the legitimate `*.ethereum.org` origins. This is a concrete allowlist bypass of the exact "insufficient fix of an origin/host whitelist" class described in the report — the whitelist is intended to scope access to a specific trusted domain family but is bypassable by any attacker who registers a lookalike domain, requiring no network privileges, no DNS control, and no victim interaction beyond visiting the attacker's page.

### Likelihood Explanation
High likelihood: registering a domain such as `evilethereum.org` or `xethereum.org` is trivial and free for any attacker, unlike the original DNS-rebinding report, which required control of DNS responses. The bypass is deterministic and requires no timing tricks, race conditions, or network-level control — a single crafted `Origin` header is sufficient.

### Recommendation
Fix the wildcard suffix check in `isAllowedOrigin` (`core/services/gateway/network/httpserver.go`) to require that the matched suffix is preceded by a literal dot, or equivalently compare on DNS-label boundaries, e.g.:

```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
(i.e., include the leading dot in the suffix comparison so `evilethereum.org` cannot match `.ethereum.org`).

### Proof of Concept
1. Configure the Gateway HTTP server with `CORSEnabled: true` and `CORSAllowedOrigins: []string{"https://*.ethereum.org"}`, matching the pattern demonstrated in [3](#0-2) .
2. From an attacker-controlled site hosted at `https://evilethereum.org`, send a cross-origin `fetch()` request to the Gateway's endpoint with header `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`, and the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker page's script to read the Gateway's JSON response in the browser — despite `evilethereum.org` never being intended as an allowed subdomain.

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

**File:** core/services/gateway/network/httpserver_test.go (L152-156)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://*.gov"})

```
