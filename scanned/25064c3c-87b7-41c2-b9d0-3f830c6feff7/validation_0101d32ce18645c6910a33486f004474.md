## Finding [1](#0-0) 

### Title
Gateway CORS Origin Allowlist Bypass via Missing Subdomain Boundary Check - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's HTTP server enforces a CORS origin allowlist so that only browser origins matching an admin-configured list (exact hosts or `*.domain` wildcards) can make credentialed cross-origin requests to the gateway. The wildcard-matching branch of `isAllowedOrigin` uses `strings.HasSuffix` without verifying a `.` boundary before the matched suffix, so any origin whose hostname merely *ends with* the allowed suffix — not just true subdomains — is accepted. This mirrors the root cause of the File Browser `CanExecute` bypass (GHSA-w7qc-6grj-w7r8): a list intended to authorize a narrow, exact set of values is implemented with unbounded substring/suffix matching instead of a boundary-safe match, letting an unprivileged, attacker-controlled value slip through the allowlist.

### Finding Description
`isAllowedOrigin` in [2](#0-1)  parses the request's `Origin` header and an admin-configured entry from `CORSAllowedOrigins`. For wildcard entries (`*.remix.com`), it strips the `*.` prefix and checks:
```go
if strings.HasSuffix(originHost, allowedHost) {
    return true
}
``` [1](#0-0) 

`strings.HasSuffix` matches any string ending with the given suffix regardless of what character precedes it. For an allowed pattern `*.remix.com` (stripped to `remix.com`), an origin host such as `evilremix.com` also satisfies `HasSuffix("evilremix.com", "remix.com")` because there is no requirement that the character immediately preceding the suffix be a literal `.`. The intended semantics ("any subdomain of remix.com") are not what is enforced; instead, "any hostname whose tail characters spell remix.com" is accepted — exactly the same class of flaw as File Browser's `CanExecute`, where an unanchored regex match let `ls` also authorize `lsof`/`lsusb`.

This check gates the response's `Access-Control-Allow-Origin` / `Access-Control-Allow-Credentials`-style headers in `handleRequest`: [3](#0-2) 
An attacker fully controls the `Origin` header from any unprivileged browser context (no credentials or prior authorization needed) and can register a domain like `evilremix.com` to pass the wildcard check intended only for `*.remix.com`.

### Impact Explanation
This is the gateway's internet-facing HTTP entrypoint (`core/services/gateway/network/httpserver.go`), used by external/browser clients to reach node-side handlers (e.g. vault, webapi triggers) via `HTTPRequestHandler.ProcessRequest`. If credentials (cookies, bearer tokens implicitly sent by the browser, or reliance on the Origin check as a CSRF-style control) are ever relied upon in conjunction with this CORS gate, a malicious website hosted on an attacker-registered domain that merely ends with the allowed suffix can have its cross-origin requests treated as though they originated from a trusted subdomain, potentially enabling cross-origin request forgery against the gateway's API from an unprivileged, unauthenticated web attacker.

### Likelihood Explanation
Exploitation only requires: (1) the operator configuring a wildcard entry in `CORSAllowedOrigins` (a documented, expected usage pattern), and (2) an attacker registering or using any domain that ends with the allowed suffix (e.g., `evilremix.com` vs. allowed `*.remix.com`), which is trivial and entirely within attacker control — no privileges or prior access to the gateway are required.

### Recommendation
Fix the wildcard match to require a `.` boundary immediately before the suffix (or split hostnames on `.` and compare labels), e.g.:
```go
if strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost {
    return true
}
```
Add regression tests analogous to the CanExecute fix in File Browser, verifying that `evilremix.com`, `notremix.com`, etc. are rejected against an allowlist entry of `*.remix.com`, while only `foo.remix.com` (and `remix.com` itself, if intended) are accepted.

### Proof of Concept
1. Configure the gateway with `CORSAllowedOrigins = ["https://*.remix.com"]` and `CORSEnabled = true`.
2. From a browser (or via `curl -H "Origin: https://evilremix.com"`), send a request to the gateway's HTTP endpoint.
3. Observe that `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilremix.com", "remix.com")` is `true`, and the response includes `Access-Control-Allow-Origin: https://evilremix.com`, even though `evilremix.com` is not a subdomain of `remix.com`.

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
