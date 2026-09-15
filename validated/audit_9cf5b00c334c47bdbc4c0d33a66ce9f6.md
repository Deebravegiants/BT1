The code confirms the claim exactly as described.

Audit Report

## Title
CORS Origin Allowlist Bypass via Improper Suffix Matching in Gateway HTTP Server - (File: core/services/gateway/network/httpserver.go)

## Summary
The `isAllowedOrigin` function in the Gateway's HTTP server validates wildcard CORS entries (e.g. `*.remix.com`) by stripping the `*.` prefix and then performing a bare `strings.HasSuffix` comparison against the request's `Origin` host, without verifying a domain-label boundary. This allows an attacker-controlled domain like `evilremix.com` to satisfy `strings.HasSuffix("evilremix.com", "remix.com")` and be treated as a trusted subdomain.

## Finding Description
In `isAllowedOrigin` [1](#0-0) , when an allowlist entry starts with `*.`, the code strips the prefix and checks `strings.HasSuffix(originHost, allowedHost)` with no check that the preceding character is a `.`. This means any origin host that merely ends with the allowed suffix — not just legitimate subdomains — passes the check. The function is called directly from `handleRequest` using the attacker-controlled `Origin` header [2](#0-1) , and upon a positive match, the header `Access-Control-Allow-Origin` is set to the attacker's own origin, granting it CORS access. There is no additional boundary check anywhere else in the file (`splitURL` only parses scheme/host/port, it does not sanitize for this issue) [3](#0-2) .

## Impact Explanation
This is a legitimate CORS allowlist bypass: an operator configuring a wildcard entry like `*.remix.com` intends to trust only genuine subdomains of `remix.com`, but the flawed suffix check also trusts unrelated domains such as `evilremix.com` or `notremix.com`. This lets a browser-based attacker hosted on such a domain interact with the Gateway's user-facing HTTP API cross-origin as if it were a trusted subdomain, exposing responses intended only for trusted origins. This maps to the in-scope "allowlist bypass / cross-user response corruption" impact category.

## Likelihood Explanation
Exploitation requires only registering a domain that happens to end with the allowlisted suffix (trivial, unprivileged DNS registration) and sending a request with a crafted `Origin` header from a browser — no authentication, node access, or privileged role required. It does require the operator to have configured a wildcard entry in `CORSAllowedOrigins`, which is a supported, documented configuration option, making this a realistic and repeatable condition rather than a purely theoretical one.

## Recommendation
Fix the wildcard host comparison to require a proper subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```

## Proof of Concept
1. Configure `CORSAllowedOrigins = ["*.remix.com"]` and `CORSEnabled = true` on the Gateway user-facing HTTP server.
2. Send an HTTP request to the Gateway endpoint with header `Origin: https://evilremix.com`.
3. Observe that `isAllowedOrigin` returns `true` (via `strings.HasSuffix("evilremix.com", "remix.com")`), and the response contains `Access-Control-Allow-Origin: https://evilremix.com`.
4. This can be verified with a Go unit test directly calling `httpServer.isAllowedOrigin("https://evilremix.com")` after configuring `CORSAllowedOrigins: []string{"*.remix.com"}`, asserting it returns `true` (bug) instead of `false` (expected/fixed behavior).

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

**File:** core/services/gateway/network/httpserver.go (L195-202)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}
```
