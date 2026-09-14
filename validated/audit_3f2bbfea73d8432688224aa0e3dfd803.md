## Finding

I found a valid analog in the chainlink gateway's CORS origin allowlist matching logic, which mirrors the same bug class as the reported Copier issue: a prefix/suffix-based "trust" match that omits a proper boundary check, allowing an attacker-controlled value to satisfy a match intended only for a specific trusted set.

### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The Gateway HTTP server's CORS origin check (`isAllowedOrigin`) treats a configured wildcard entry like `*.trusted.org` as matching any origin hostname that merely ends with the string `trusted.org`, without requiring a `.` (label) boundary before the suffix. An attacker who registers a domain such as `eviltrusted.org` can therefore satisfy the wildcard check meant to trust only actual subdomains of `trusted.org`.

### Finding Description
`isAllowedOrigin` performs the wildcard match like this: [1](#0-0) 

`allowedHost` is stripped of its `*.` prefix (e.g. `*.trusted.org` → `trusted.org`), and then compared using `strings.HasSuffix(originHost, allowedHost)`. This is a raw substring-suffix comparison with no normalization of segment boundaries — exactly the same class of defect as the Copier `trust` prefix check, which used raw `str.startswith` on an unnormalized path/URL and let a value that "textually" looked trusted pass the check while actually referring to a different location. Here, an origin such as `https://eviltrusted.org` ends with `trusted.org` textually, so it is granted the same CORS trust as legitimate subdomains like `https://api.trusted.org`, even though it is not part of that domain at all.

The comparison inputs are lowercased and parsed via `url.Parse` in `splitURL` [2](#0-1) , but no dot-boundary check is added before the suffix comparison, so this is not a normalization artifact of a resolver — it's a missing anchor character (`.`) in the match itself.

The gating result directly controls whether the gateway echoes back `Access-Control-Allow-Origin` for the caller's `Origin` header and enables cross-origin reads of the JSON-RPC response body: [3](#0-2) 

This handler is the entry point for the internet-facing gateway's JSON-RPC request processing, used by handlers such as the Vault gateway handler (`core/capabilities/vault/gw_handler.go`) and the HTTP capability handler (`core/services/gateway/handlers/capabilities/v2/http_handler.go`), which return sensitive per-caller data (e.g. authorized secrets metadata, workflow-scoped responses).

### Impact Explanation
Any operator who configures a wildcard CORS entry (e.g. `*.mycompany.com`), intending to trust only genuine subdomains, unintentionally also trusts any domain that happens to end in the same string (e.g. an attacker-registered `evilmycompany.com`). A malicious website hosted on such a domain can issue authenticated cross-origin browser requests to the gateway and read back JSON-RPC responses that were only meant to be readable by the legitimate trusted origin — a cross-user/cross-origin response confusion and CORS allowlist bypass, unprompted by any explicit trust decision beyond the operator's original (narrower) wildcard intent.

### Likelihood Explanation
Exploitation requires: (1) the gateway operator has `CORSEnabled` with at least one wildcard entry `*.<suffix>` configured, and (2) a victim's browser to visit an attacker page while a session/credential exists for the trusted origin's use of the gateway. Both are realistic operational configurations; wildcard CORS entries are a documented, supported feature. Domain registration matching a suffix is trivial for an attacker to obtain.

### Recommendation
Anchor the wildcard suffix match on a label boundary: after stripping `*.`, require that `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`. This mirrors the fix recommended for the Copier issue — normalize/anchor before doing prefix/suffix trust comparisons rather than doing raw string containment checks.

### Proof of Concept
1. Configure the gateway with `CORSEnabled: true` and `CORSAllowedOrigins: ["*.trusted.org"]`.
2. From a browser page hosted at `https://eviltrusted.org`, send a cross-origin request to the gateway's configured `Path` with header `Origin: https://eviltrusted.org`.
3. Observe that `isAllowedOrigin` returns `true` (since `"eviltrusted.org"` has suffix `"trusted.org"`), and the response includes `Access-Control-Allow-Origin: https://eviltrusted.org`, letting the attacker page read the JSON-RPC response body via `fetch`/XHR, despite `eviltrusted.org` never being an intended subdomain of `trusted.org`. [4](#0-3)

### Citations

**File:** core/services/gateway/network/httpserver.go (L138-155)
```go
func (s *httpServer) splitURL(rawURL string) (string, string, string, error) {
	// lowercase the URL to avoid case sensitivity issues
	parsedURL, err := url.Parse(strings.ToLower(rawURL))
	if err != nil {
		return "", "", "", fmt.Errorf("error parsing URL: %w", err)
	}

	host, port, err := net.SplitHostPort(parsedURL.Host)
	if err != nil {
		// if there's no port, the host itself is returned
		if parsedURL.Host != "" {
			return parsedURL.Scheme, parsedURL.Host, "", nil
		}
		return "", "", "", fmt.Errorf("error splitting host and port: %w", err)
	}

	return parsedURL.Scheme, host, port, nil
}
```

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
