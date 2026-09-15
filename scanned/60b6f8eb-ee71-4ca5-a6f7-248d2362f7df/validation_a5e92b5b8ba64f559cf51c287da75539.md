I found a genuine analog. The Chainlink Gateway's user-facing HTTP server implements its own CORS origin validation in `core/services/gateway/network/httpserver.go`, and the wildcard-matching logic contains a domain-suffix boundary bug that allows unauthorized origins to be treated as trusted — the same root-cause bug class as CVE-2025-50579 (improper Origin validation leading to unauthorized cross-origin access).

### Title
CORS wildcard origin matching allows domain-suffix spoofing bypass in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's `UserServerConfig` HTTP endpoint (`core/services/gateway/network/httpserver.go`) implements a custom CORS allow-list check, `isAllowedOrigin`, supporting wildcard subdomain entries like `*.example.com`. The wildcard-matching logic strips the `*.` prefix and then does a raw string-suffix comparison against the request's `Origin` header host, without verifying a literal dot boundary before the suffix. As a result, an attacker-controlled domain that merely *ends with* the same characters as the allowed suffix (but is not actually a subdomain) is incorrectly treated as an allowed origin.

### Finding Description
The vulnerable logic is: [1](#0-0) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

If an operator configures `CORSAllowedOrigins = ["https://*.ethereum.org"]` (a pattern used in this codebase's own tests, see `httpserver_test.go`), the check strips the wildcard to get `ethereum.org` and then only verifies that the request's `Origin` host string ends with `ethereum.org` — with no requirement for a `.` immediately preceding it. A malicious domain such as `https://fakeethereum.org` (or any domain an attacker registers ending in the literal characters `ethereum.org`, e.g. `evilethereum.org`) will pass `strings.HasSuffix("fakeethereum.org", "ethereum.org")` and be granted `Access-Control-Allow-Origin` reflection, even though it is a completely unrelated, attacker-controlled domain rather than a legitimate subdomain.

This is invoked from the request-handling path: [2](#0-1) 

Once `isAllowedOrigin` returns true, the server reflects the attacker's `Origin` value directly into `Access-Control-Allow-Origin`, and the request path also extracts and forwards the caller's `Authorization: Bearer` JWT token to the handler, and returns the JSON-RPC response body to the browser — meaning any sensitive data or session-bound response returned by `ProcessRequest` becomes readable by script running on the attacker's spoofed-suffix domain via a standard cross-origin fetch/XHR with credentials.

### Impact Explanation
This affects the Gateway's user-facing HTTP server, the component intended to accept unauthenticated/unprivileged client HTTP requests. An attacker who registers a domain string that merely ends with an allowed wildcard suffix (no subdomain relationship required) can trick a victim's browser into making authenticated cross-origin requests to the Gateway and read the JSON responses, which may include JWT-bearing bridge/job-run data or othersensitive response content — directly mirroring the CVE-2025-50579 impact of token interception via CORS misconfiguration.

### Likelihood Explanation
Exploitation requires: (1) the Gateway operator having configured at least one wildcard `CORSAllowedOrigins` entry with `CORSEnabled = true`, and (2) the attacker registering/controlling a domain whose string happens to end with the configured suffix. Since domain names ending in a given string are trivially obtainable (e.g., register `notethereum.org` to bypass `*.ethereum.org`), likelihood is realistic wherever wildcard CORS entries are used, though it depends on this non-default configuration choice.

### Recommendation
Fix the suffix check to require a dot boundary, e.g.:
```go
if strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost {
    return true
}
```
This ensures `fakeethereum.org` no longer matches `*.ethereum.org`, while legitimate subdomains like `remix.ethereum.org` continue to match.

### Proof of Concept
1. Configure the Gateway's `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser on attacker-controlled `https://fakeethereum.org`, send a `fetch` request with `credentials: 'include'` to the Gateway's user endpoint, setting `Origin: https://fakeethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://fakeethereum.org`, since `strings.HasSuffix("fakeethereum.org", "ethereum.org")` evaluates true in `isAllowedOrigin` (`core/services/gateway/network/httpserver.go:184-190`).
4. The attacker's script can now read the JSON-RPC response body cross-origin, including any JWT or sensitive payload data returned by `ProcessRequest`.

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
