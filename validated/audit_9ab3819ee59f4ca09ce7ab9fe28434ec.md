## Finding: Wildcard CORS origin bypass in Gateway HTTP server

The Gateway's `isAllowedOrigin` wildcard matching logic has the same class of flaw as the Phoenix `check_origin` bug: it uses a plain string-suffix comparison for wildcard hosts instead of verifying a subdomain boundary. [1](#0-0) 

### Title
CORS wildcard origin bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
`httpServer.isAllowedOrigin` implements wildcard-domain matching (`*.example.com`) for the `CORSAllowedOrigins` config by stripping the `*.` prefix and checking `strings.HasSuffix(originHost, allowedHost)`. This is not anchored to a subdomain (`.`) boundary, so any origin whose hostname merely *ends with* the allowed suffix — not just true subdomains — is accepted.

### Finding Description [2](#0-1) 

The relevant code:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
If an operator configures `CORSAllowedOrigins = ["https://*.example.com"]` intending to allow only subdomains of `example.com`, the check reduces to `strings.HasSuffix(originHost, "example.com")`. Any attacker-registered domain ending in that literal string — with no dot separator required — passes, e.g. `evilexample.com`, `notexample.com`, or `fakeexample.com`. These are not subdomains of `example.com` at all, they are unrelated domains an attacker fully controls, yet they satisfy the suffix check. This directly mirrors the Phoenix advisory's root cause: naive suffix-based wildcard origin matching without boundary anchoring (CWE-346/CWE-863).

This check gates the `Access-Control-Allow-Origin` response header set in `handleRequest`, which is reachable by any unprivileged/unauthenticated web client hitting the internet-facing Gateway user-server endpoint. [3](#0-2) 

### Impact Explanation
An attacker who controls a domain such as `evilexample.com` can host a malicious webpage there. When a victim's browser (already having an authenticated session/cookie or bearer token usable against the Gateway) visits that page, cross-origin JavaScript can issue credentialed requests to the Gateway's user-facing HTTP API. Because the origin passes `isAllowedOrigin`, the server reflects `Access-Control-Allow-Origin: https://evilexample.com`, letting the browser read the JSON-RPC response — enabling data exfiltration / request forgery against the Gateway API from a domain the operator never intended to trust.

### Likelihood Explanation
Exploitability depends on an operator using a wildcard entry (e.g. `*.some-trusted-domain.com`) in `CORSAllowedOrigins`/`config.CORSEnabled = true` for the Gateway's `UserServerConfig`, which is a documented and tested configuration pattern (see `core/services/gateway/integration_tests/gateway_integration_test.go` using `CORSAllowedOrigins = ["https://remix.ethereum.org"]`, and wildcard support is explicitly implemented and tested in `isAllowedOrigin`/its test file). Any operator relying on wildcard CORS for the gateway is exposed; no privileged access or special node/peer status is required, only registering a look-alike domain.

### Recommendation
Anchor wildcard suffix matching to a subdomain boundary — require that `originHost` either equals `allowedHost` (root domain) or ends with `"."+allowedHost`, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    base := allowedHost[2:]
    if originHost == base || strings.HasSuffix(originHost, "."+base) {
        return true
    }
}
```

### Proof of Concept
1. Configure Gateway `UserServerConfig`: `CORSEnabled = true`, `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Send a request with header `Origin: https://evilexample.com`.
3. Observe response header `Access-Control-Allow-Origin: https://evilexample.com` is set (per `handleRequest`/`isAllowedOrigin` logic at lines 157-209), even though `evilexample.com` is not a subdomain of `example.com`.

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
