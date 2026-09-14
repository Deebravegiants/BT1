I have sufficient evidence to confirm this analog vulnerability.

### Title
CORS wildcard origin allowlist bypass via unbounded suffix match - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The Chainlink Gateway's public-facing user HTTP server (`core/services/gateway/network/httpserver.go`) validates the `Origin` header against a configured allowlist to decide whether to echo it back in `Access-Control-Allow-Origin`. For wildcard entries (e.g. `*.remix.com`), the code strips the `*.` prefix and then performs a raw `strings.HasSuffix` comparison with no domain-boundary (dot) check, mirroring the same class of unsafe substring/suffix host-matching bug described in the cdxgen advisory (GHSA-qhh4-458h-xwh2), where `serverAddress.includes(forRegistry)` incorrectly matched hosts that merely contain the target as a substring instead of validating them as a proper origin/host.

### Finding Description
In `isAllowedOrigin`, wildcard matching is implemented as: [1](#0-0) 

`allowedHost` is derived by stripping the `*.` prefix (e.g., `*.remix.com` → `remix.com`), and the match is `strings.HasSuffix(originHost, allowedHost)`. This check has no dot-boundary requirement between the stripped allowed suffix and the rest of `originHost`. Consequently, an attacker-controlled origin such as `https://evilremix.com` satisfies `strings.HasSuffix("evilremix.com", "remix.com") == true`, even though `evilremix.com` is not a subdomain of `remix.com` at all — it is an unrelated domain that happens to share a trailing substring. This is exactly the CWE-346 "origin validation error" pattern in the advisory: a substring/suffix comparison is used where a strict, boundary-aware host/origin comparison is required.

The scheme and port are checked exactly (`originScheme != allowedScheme`, `originPort != allowedPort`), and the exact-host case (`originHost == allowedHost`) is correctly implemented, but the wildcard branch alone lacks the boundary check. This is reachable directly from the internet-facing Gateway user HTTP server (`httpServer.handleRequest`), which any unauthenticated remote browser client can hit by sending a crafted `Origin` header: [2](#0-1) 

### Impact Explanation
When `CORSEnabled` is true and an operator configures a wildcard entry (e.g., `*.mycompany.com`) intending to scope browser access to their own subdomains, an attacker who registers a domain that merely ends with that suffix (e.g., `evilmycompany.com`, or more realistically `notmycompany.com` if the allowed suffix were `.com`-adjacent, or any crafted domain ending in the same characters) can have their origin accepted. The server then reflects that origin in `Access-Control-Allow-Origin`, allowing a malicious webpage to make authenticated/JSON-RPC cross-origin requests to the Gateway's user-facing API (workflows/vault handlers reachable via `gateway.ProcessRequest`) and read the responses in-browser, bypassing the intended origin restriction. This is a concrete allowlist-bypass in the internet-facing gateway (CWE-346), matching the accepted analog categories.

### Likelihood Explanation
Exploitability only requires: (1) the operator has `CORSEnabled = true` with at least one wildcard entry in `CORSAllowedOrigins` (a documented, supported configuration pattern, exercised in `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`), and (2) an attacker who can register/control a domain string ending in the same characters as the allowed suffix and can lure a victim's browser (with access to the Gateway) to visit it. No privileged access or node compromise is needed — this is purely an unprivileged client-side request against the public Gateway endpoint.

### Recommendation
Fix the wildcard comparison in `isAllowedOrigin` to require a domain boundary, e.g. verify `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix`, so `evilremix.com` no longer matches an allowlist entry of `*.remix.com`.

### Proof of Concept
Given Gateway config:
```toml
CORSEnabled = true
CORSAllowedOrigins = ["https://*.remix.com"]
```
An attacker-controlled page hosted at `https://evilremix.com` sends a cross-origin `fetch` to the Gateway's `/user` endpoint with header `Origin: https://evilremix.com`. Tracing `isAllowedOrigin`:
- `originHost = "evilremix.com"`, `allowedHost` after stripping `*.` = `"remix.com"`.
- `strings.HasSuffix("evilremix.com", "remix.com")` → `true`.

The server responds with `Access-Control-Allow-Origin: https://evilremix.com`, and the browser permits the attacker page to read the response, even though `evilremix.com` is not a legitimate subdomain of `remix.com`. [3](#0-2)

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
