### Title
CORS origin allowlist bypass via unanchored suffix matching in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's HTTP server implements a wildcard CORS origin check (`*.domain.com`) by stripping the `*.` prefix and testing whether the incoming `Origin` header's host ends with the configured suffix using `strings.HasSuffix`, without requiring a `.` boundary before the match. This mirrors the NextChat CVE-2026-82639 root cause: validating an attacker-controlled string with substring/suffix matching instead of proper hostname parsing, letting any host that merely *contains* the allowed suffix pass validation.

### Finding Description
In `isAllowedOrigin`, wildcard entries in `CORSAllowedOrigins` (e.g. `*.remix.ethereum.org`) are checked with: [1](#0-0) 

`allowedHost` becomes `ethereum.org` after stripping `*.`, and the code only verifies `strings.HasSuffix(originHost, allowedHost)` — it never checks that the character preceding the matched suffix is a `.` (or that the match starts at a label boundary). As a result, an operator-configured wildcard like `*.ethereum.org` also matches attacker-registered domains such as `evilethereum.org` or `notethereum.org`, because those strings end with the literal bytes `ethereum.org` with no dot separator required.

This is functionally identical to the NextChat bug class described in the report: the `x-base-url` header there was validated with `Contains("api.openai.com")` instead of parsing the URL's actual host, letting `evilapi.openai.com.attacker.com`-style strings slip past validation. Here, the equivalent flaw is `HasSuffix(originHost, allowedHost)` without label-boundary checking, in the internet-facing Gateway HTTP server that any unauthenticated client can reach by simply sending an `Origin` header.

The comparison happens on `originHost`/`allowedHost` returned by `splitURL`, which uses `url.Parse` + `net.SplitHostPort` correctly for structural parsing, but the wildcard branch throws that correctness away by falling back to a naive string suffix check: [2](#0-1) 

The result of `isAllowedOrigin` directly controls whether the server echoes the attacker's `Origin` value into `Access-Control-Allow-Origin`: [3](#0-2) 

### Impact Explanation
Any operator who configures a wildcard CORS entry (e.g. `*.ethereum.org`, `*.mycompany.com`) intending to scope browser access to their own subdomains unintentionally also grants CORS access to any domain an attacker can register that ends in that literal string without a preceding dot (e.g. `evilethereum.org`, `notmycompany.com`). A malicious website hosted on such a domain can issue cross-origin `fetch`/`XHR` requests to the Gateway and have its JavaScript read the JSON-RPC response body that the browser would otherwise block under the Same-Origin Policy — this is a concrete allowlist bypass causing cross-user/cross-origin response confusion at the gateway boundary, matching the "allowlist bypass" / "cross-user response confusion" impact classes.

### Likelihood Explanation
Exploitation requires only that: (1) the Gateway operator has CORS enabled with at least one wildcard entry (a documented, supported configuration, not a misconfiguration by itself), and (2) an attacker registers or already controls a domain that ends with the configured suffix without a dot boundary — a cheap and realistic step (many such suffix-colliding domain names are readily available). No authentication or privileged access is needed; the attacker only needs to lure a victim's browser to their page and issue a cross-origin request with a crafted `Origin` header (which browsers set automatically and cannot be spoofed by script, but the attacker fully controls their own page's origin).

### Recommendation
Fix the wildcard match to require a `.` immediately before the suffix (or equivalently, split `originHost` on `.` and compare the trailing labels), e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[2:]
    if originHost == suffix || strings.HasSuffix(originHost, "."+suffix) {
        return true
    }
}
```
This ensures `evilethereum.org` no longer matches `*.ethereum.org`, while legitimate subdomains like `remix.ethereum.org` continue to match.

### Proof of Concept
1. Start the Gateway HTTP server with CORS enabled and `CORSAllowedOrigins: []string{"https://*.ethereum.org"}` (as validated by `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`, `core/services/gateway/network/httpserver_test.go:152-186`).
2. From a browser page hosted at `https://evilethereum.org`, send a POST request to the Gateway's configured path with header `Origin: https://evilethereum.org`.
3. Observe the server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, because `isAllowedOrigin` computes `originHost = "evilethereum.org"`, `allowedHost = "ethereum.org"`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.
4. The attacker's page JavaScript can now read the Gateway's JSON-RPC response cross-origin, despite not being an intended subdomain of `ethereum.org`. [2](#0-1)

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
