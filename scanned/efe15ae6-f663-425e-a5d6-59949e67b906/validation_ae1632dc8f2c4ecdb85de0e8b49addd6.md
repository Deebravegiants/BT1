## Analysis

I examined the CORS/origin-allowlist logic in the gateway's public-facing HTTP server, which is the internet-facing entry point analogous to the "no-auth, browser-reachable" surface described in the homepage DNS-rebinding report. [1](#0-0) 

### Title
CORS wildcard-origin allowlist bypass via missing subdomain boundary check - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's public HTTP server validates cross-origin requests against an operator-configured allowlist (`CORSAllowedOrigins`). For wildcard entries (`*.example.com`), the check uses a raw `strings.HasSuffix` comparison without verifying a `.` boundary before the matched suffix, allowing any hostname that merely ends with the configured suffix string (not just true subdomains) to be treated as an allowed origin.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard origin and then checks `strings.HasSuffix(originHost, allowedHost)`. [2](#0-1) 

Because this is a plain string suffix check rather than a label-boundary-aware subdomain check, a host like `evil-remix.ethereum.org` (an attacker-registrable, unrelated hostname) will incorrectly satisfy `HasSuffix("evil-remix.ethereum.org", "remix.ethereum.org")` and be treated as a legitimate subdomain of an operator-intended wildcard `*.remix.ethereum.org`. The same pattern applies to any wildcard-configured allowed origin, e.g. `*.example.com` would also match attacker domain `evilexample.com`.

This is invoked in `handleRequest`, where a matching origin causes the server to echo it back in `Access-Control-Allow-Origin`, permitting the attacker's page to read the JSON-RPC response cross-origin: [3](#0-2) 

The Gateway is the internet/browser-facing endpoint that proxies authenticated JSON-RPC (e.g., vault secret operations gated by allowlist/JWT authorization further downstream), so an Origin-check bypass undermines the intended trust boundary that the allowlist is supposed to enforce, similarly to how the reported CVE undermines the boundary a browser's same-origin policy is supposed to enforce against an internal, unauthenticated service.

### Impact Explanation
If an operator configures a wildcard `CORSAllowedOrigins` entry (as the code explicitly supports and documents as a supported pattern), any attacker who registers a lookalike domain ending in the same suffix string can have their web page read cross-origin JSON-RPC responses from the Gateway that browsers would otherwise block via the Same-Origin Policy. Depending on what data is returned by whichever handler is registered (`HTTPRequestHandler.ProcessRequest`), this could expose response contents (e.g., authorization/allowlist results, error details) to an unintended origin — an allowlist-bypass class issue per the validation criteria.

### Likelihood Explanation
Exploitability depends on the operator using a wildcard entry in `CORSAllowedOrigins` (supported and documented usage), and on an attacker being able to register a hostname that string-suffix-matches the configured wildcard. This is a known, well-documented class of CORS misconfiguration bug and requires no special network position — an unprivileged actor need only get a victim (or their own browser) to send a request with a crafted `Origin` header to the exposed Gateway port.

### Recommendation
Replace the raw suffix check with a proper subdomain-boundary comparison, e.g. require that `originHost` equals `allowedHost` or ends with `"."+allowedHost`:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```

### Proof of Concept
1. Operator configures `CORSAllowedOrigins = ["*.remix.ethereum.org"]` for the Gateway.
2. Attacker registers `evil-remix.ethereum.org` (or any hostname ending in the literal string `remix.ethereum.org`) and serves a page from it.
3. Attacker's page issues a `fetch()`/`XMLHttpRequest` to the Gateway's HTTP endpoint with `Origin: https://evil-remix.ethereum.org`.
4. `isAllowedOrigin` returns `true` due to the unbounded `strings.HasSuffix` check; the server responds with `Access-Control-Allow-Origin: https://evil-remix.ethereum.org`.
5. The browser permits the attacker's JavaScript to read the response body, bypassing the operator's intended origin restriction.

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
