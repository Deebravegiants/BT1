## Analysis

The external report describes a **host-confusion vulnerability**: a URI parser accepts a malformed/ambiguous host string and callers make authorization/allowlist decisions based on the parser's interpretation, while a different, later parser resolves the same string to a different host. The chainlink Go codebase does not depend on `fast-uri` (it is a JS library), and Go's standard `net/url` package's bracket-handling in `parseHost` rejects genuinely unbalanced IPv6 brackets rather than silently accepting them, so the literal vulnerability class is not reproducible via Go's `url.Parse`. However, there is a directly analogous **host-matching/allowlist bug** in the gateway's CORS origin check that is reachable from any unprivileged network client.

### Root cause
`isAllowedOrigin` in [1](#0-0)  parses the client-supplied `Origin` header and an allowlist entry via `splitURL` (which wraps `url.Parse` + `net.SplitHostPort`, see [2](#0-1) ), then performs a wildcard match using an unanchored suffix comparison:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [3](#0-2) 

For an allowlist entry like `*.remix.com`, `allowedHost` becomes `remix.com`, and `strings.HasSuffix` matches any origin host that merely *ends with* `remix.com` — with no required `.` boundary. An attacker-registered domain such as `evilremix.com` or `notremix.com` therefore matches the same suffix and is treated as an allowed origin, which is the same class of bug as the fast-uri issue: a host string is judged as belonging to a trusted set based on a naive/incomplete check, causing the security decision to diverge from the true host identity.

### Reachability and impact
`isAllowedOrigin` is invoked directly on the attacker-controlled `Origin` request header in `handleRequest` [4](#0-3) , which is the gateway's internet-facing HTTP entrypoint used for workflow trigger requests (`HTTPRequestHandler.ProcessRequest`) [5](#0-4) . Since it is only reached when `CORSEnabled` is true and the operator configures an origin allowlist (`*.domain.com` wildcard entries), any unprivileged attacker who can lure a victim's browser to a domain like `evilremix.com` bypasses the intended origin restriction; the server reflects the attacker's origin back as `Access-Control-Allow-Origin` [6](#0-5) , enabling cross-origin reading of gateway JSON-RPC responses that a legitimate `*.remix.com` subdomain was meant to be trusted with.

### Title
Improper suffix-only wildcard host matching in gateway CORS `Origin` allowlist enables cross-origin bypass - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The gateway's CORS wildcard origin match (`*.example.com`) uses `strings.HasSuffix` without verifying a preceding `.` (domain-label boundary), so any attacker-controlled domain ending in the same characters (e.g. `evilexample.com`) is incorrectly treated as a trusted subdomain.

### Finding Description
`isAllowedOrigin` [1](#0-0)  strips the `*.` prefix from a configured allowed origin and checks `strings.HasSuffix(originHost, allowedHost)`. This check does not require that the matched suffix begin at a label boundary, so `evilremix.com` incorrectly satisfies a `*.remix.com` allowlist entry, just as `fast-uri`'s unbalanced-bracket bug let a malformed host be treated as valid input that diverges from the actual host semantics.

### Impact Explanation
An attacker who registers a domain sharing the configured suffix can have their site's `Origin` accepted by the gateway. The server then reflects that origin into `Access-Control-Allow-Origin` [7](#0-6) , allowing the attacker's page (loaded by any victim browser with network access to the gateway) to make cross-origin credentialed/authenticated requests to the workflow-trigger JSON-RPC endpoint and read the responses — an allowlist bypass leading to cross-origin response disclosure for the gateway's HTTP trigger API.

### Likelihood Explanation
Exploitation requires only that the operator configure a wildcard CORS allowlist entry (a documented, supported configuration) and that the attacker register/control a domain with the matching suffix — no privileged access is required, only luring a victim to a malicious webpage.

### Recommendation
Change the wildcard match to require a dot boundary, e.g. `strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost`, or parse into DNS labels and compare per-label equality of the trailing labels rather than raw string suffix comparison.

### Proof of Concept
1. Configure `CORSAllowedOrigins = ["https://*.remix.com"]` and enable `CORSEnabled`.
2. Send a request to the gateway HTTP endpoint with header `Origin: https://evilremix.com`.
3. Observe `isAllowedOrigin` returns `true` and the response includes `Access-Control-Allow-Origin: https://evilremix.com`, even though `evilremix.com` is not a subdomain of `remix.com`.

### Citations

**File:** core/services/gateway/network/httpserver.go (L33-35)
```go
type HTTPRequestHandler interface {
	ProcessRequest(ctx context.Context, rawMessage []byte, auth string) (rawResponse []byte, httpStatusCode int)
}
```

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
