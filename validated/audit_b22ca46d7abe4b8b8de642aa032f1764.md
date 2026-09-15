Audit Report

## Title
CORS wildcard origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` validates wildcard CORS entries (e.g. `https://*.remix.org`) using a raw `strings.HasSuffix(originHost, allowedHost)` check after stripping the `*.` prefix, with no re-anchoring on a `.` boundary. As a result, an attacker-controlled origin such as `https://evilremix.org` incorrectly passes as a match for the allowed wildcard `*.remix.org`, because `strings.HasSuffix("evilremix.org", "remix.org")` is true even though `evilremix.org` is not a subdomain of `remix.org`.

## Finding Description
The relevant logic: [1](#0-0) . Both origin and allowed origin are parsed via `splitURL` (using `url.Parse` + `net.SplitHostPort`) [2](#0-1) , so scheme/host/port are correctly separated, but the wildcard-host comparison itself only checks that `originHost` ends with the trusted suffix as a raw string, without requiring the preceding character to be `.` or the match to be exact. This is confirmed to be reachable from `handleRequest`, which reflects the attacker-supplied `Origin` header value directly into `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true, and also sets permissive `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers` [3](#0-2) . This is on the Gateway's public, unauthenticated HTTP endpoint registered in `NewHTTPServer` [4](#0-3) , reachable by any client that can send an HTTP request with a spoofed `Origin` header — no authentication or special network position required. No other validation logic anchors the suffix match on a subdomain label boundary, so the flaw is real and unmitigated by surrounding code.

Note: the server does not set `Access-Control-Allow-Credentials`, so this does not enable automatic cookie-based credentialed cross-origin requests (the Gateway authenticates via a `Bearer` JWT extracted from the `Authorization` header, not cookies) [5](#0-4) . However, the browser Same-Origin Policy read-blocking is still bypassed for non-credentialed requests: an attacker page hosted on a look-alike domain (e.g. `evilremix.org`) can issue a `fetch`/`XHR` to the Gateway and have the browser permit reading the JSON response, something the operator's `*.remix.org`-scoped allowlist was intended to prevent.

## Impact Explanation
This breaks the intended CORS allowlist trust boundary: a domain the operator did not intend to trust (anything ending in the configured suffix, e.g. `evilremix.org`, `attacker-remix.org`) can be granted the same CORS read access as a genuine subdomain of the trusted domain. This maps to the in-scope "allowlist bypass" impact category. The severity is bounded by the fact that no credentials header is set (so cookie-based session hijacking is not directly enabled) and the Gateway's actual authorization relies on a bearer JWT the attacker page would still need to independently obtain/possess, but it is a genuine, code-level defect that defeats a documented security control (`CORSAllowedOrigins` wildcarding) as described in `sample_config.toml`.

## Likelihood Explanation
Exploitation only requires: (1) the operator to configure a wildcard `CORSAllowedOrigins` entry — a normal, documented, supported feature rather than a misconfiguration — and (2) an attacker who controls any domain name ending with the trusted suffix (cheap and easy to register, e.g. `evilremix.org` for a trusted `remix.org`). No authentication, elevated privilege, or special network position is needed; the attacker only needs to control the `Origin` header of an HTTP/browser request, which is standard capability for any web client. This is repeatable and deterministic.

## Recommendation
Anchor the suffix comparison to a proper subdomain boundary, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
This ensures `evilremix.org` does not match `*.remix.org` while genuine subdomains like `sub.remix.org` still do. As a general principle, avoid bare `HasPrefix`/`HasSuffix` for security-relevant host/origin comparisons; always validate against label (`.`) boundaries.

## Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.org"]`.
2. Send `GET /<gateway-path>` with header `Origin: https://evilremix.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.org` (and permissive `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`), because `isAllowedOrigin` at `core/services/gateway/network/httpserver.go:185-190` returns `true` via `strings.HasSuffix("evilremix.org", "remix.org")`, despite `evilremix.org` not being a subdomain of `remix.org`.
4. A unit test asserting `isAllowedOrigin("https://evilremix.org")` returns `false` when `CORSAllowedOrigins = ["https://*.remix.org"]` will fail against current code, confirming the bypass.

### Citations

**File:** core/services/gateway/network/httpserver.go (L107-114)
```go
	mux := http.NewServeMux()
	var handler http.Handler
	handler = http.HandlerFunc(server.handleRequest)
	if config.RequestTimeoutMillis > 0 {
		handler = http.TimeoutHandler(handler, time.Duration(config.RequestTimeoutMillis)*time.Millisecond, "Request timed out")
	}
	mux.Handle(config.Path, handler)
	mux.Handle(HealthCheckPath, http.HandlerFunc(server.handleHealthCheck))
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

**File:** core/services/gateway/network/httpserver.go (L226-231)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}
```
