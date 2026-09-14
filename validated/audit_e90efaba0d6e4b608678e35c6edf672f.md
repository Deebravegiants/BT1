### Title
CORS `Access-Control-Allow-Origin` allowlist bypass via unanchored suffix match in `isAllowedOrigin` - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Gateway's internet-facing HTTP server checks whether an incoming `Origin` header is allowed by comparing it against configured `CORSAllowedOrigins`. For wildcard entries (e.g. `*.remix.com`), the check strips the `*.` prefix and then uses `strings.HasSuffix(originHost, allowedHost)` with no domain-label boundary (no check that the character preceding the matched suffix is a `.`). This is the same class of bug as the reported `potato-annotation` advisory: a boundary check implemented as a raw string containment/prefix-suffix test instead of a proper structural (path/domain) boundary check, allowing values that merely *share a string suffix/prefix* with the intended value to pass validation.

### Finding Description
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements the wildcard-origin check as: [1](#0-0) 

`allowedHost` is derived by trimming the literal `*.` from a configured entry like `*.remix.com`, leaving `remix.com`, and then `strings.HasSuffix(originHost, allowedHost)` is used to decide the match. Because this is a plain string suffix test, any origin host that ends with the literal substring `remix.com` — including `evilremix.com`, `attacker-remix.com`, or `notremix.com` — will satisfy the check, even though these are not subdomains of `remix.com` and were never intended to be trusted.

This mirrors the root cause pattern in the reported advisory: `startswith()`/`HasSuffix()` used directly on unstructured strings for a security boundary decision, rather than validating on a proper separator-bounded basis (e.g., requiring the character immediately preceding the matched suffix to be `.`, or splitting on `.` and comparing labels).

### Impact Explanation
This check gates the CORS `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers` response headers on the Gateway's internet-facing HTTP server (unauthenticated request path — this is the front door that accepts client HTTP requests before dispatching to `HTTPRequestHandler.ProcessRequest`): [2](#0-1) 

If an operator configures a wildcard allowlist entry such as `*.remix.com` intending to trust only genuine subdomains of `remix.com`, an attacker who registers a domain such as `evilremix.com` (no subdomain relationship at all) can send cross-origin browser requests to the Gateway and receive `Access-Control-Allow-Origin: https://evilremix.com` in the response. A page hosted on the attacker's domain can then read Gateway JSON-RPC responses via `fetch()`/XHR that were only meant to be readable by trusted first-party or partner domains, which is an allowlist bypass in an internet-facing component (matches the accepted category: "allowlist ... bypass" in the gateway).

### Likelihood Explanation
Likelihood is moderate: it requires (a) an operator to configure a wildcard CORS origin entry, which is a documented supported feature (see `sample_config.toml` and `sample_config_tls.toml` referencing `CORSAllowedOrigins`), and (b) an unprivileged attacker to register/control a domain that happens to end with the allowed suffix. Domain registration is trivial and cheap for an attacker who wants to specifically target a known Gateway deployment that publishes its allowed wildcard domain (e.g. `*.remix.com` for a known dApp partner), making this practically exploitable once the target's config is known.

### Recommendation
Change the wildcard match in `isAllowedOrigin` to enforce a label boundary instead of a raw suffix check — e.g. require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` after stripping `*.`, so that only genuine subdomains (`foo.remix.com`) match and impostor domains sharing only a string suffix (`evilremix.com`) are rejected.

### Proof of Concept
```go
// core/services/gateway/network/httpserver.go, isAllowedOrigin()
// Configured: CORSAllowedOrigins = []string{"https://*.remix.com"}
// allowedHost after stripping "*." => "remix.com"

originHost := "evilremix.com"          // attacker-controlled domain, NOT a subdomain of remix.com
strings.HasSuffix(originHost, "remix.com") // => true, bypasses the intended allowlist boundary
```
An attacker hosting a page on `https://evilremix.com` sends a cross-origin request with `Origin: https://evilremix.com` to the Gateway's HTTP endpoint; `handleRequest` calls `isAllowedOrigin` which returns `true`, causing the server to reflect `Access-Control-Allow-Origin: https://evilremix.com` in the response: [3](#0-2) 
letting the attacker's page read the Gateway's response cross-origin.

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
