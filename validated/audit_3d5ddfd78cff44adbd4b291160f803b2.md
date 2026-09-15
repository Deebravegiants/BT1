Audit Report

## Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` matches wildcard `CORSAllowedOrigins` entries (e.g. `*.ethereum.org`) using a raw `strings.HasSuffix` check with no subdomain-boundary validation, so any attacker-controlled domain that merely ends with the configured suffix string (e.g. `evilethereum.org`) is treated as an allowed subdomain. This lets an attacker who registers such a domain get their origin reflected in `Access-Control-Allow-Origin` and read cross-origin gateway responses.

## Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard entry and then checks `strings.HasSuffix(originHost, allowedHost)` with no requirement that the matched suffix be preceded by a `.` boundary in `originHost`: [1](#0-0) . Consequently, for an allowlist entry `*.ethereum.org`, the check reduces to `strings.HasSuffix(originHost, "ethereum.org")`, which is true for `evilethereum.org` or `notethereum.org` — domains that are not subdomains of `ethereum.org` at all, just strings sharing a common suffix.

This function is called directly on the untrusted `Origin` header inside `handleRequest`, and when it returns `true` the server reflects the attacker-controlled origin verbatim into `Access-Control-Allow-Origin`: [2](#0-1) . No other validation (e.g., checking for a `.` immediately before the matched suffix, or comparing against a normalized `".suffix"` string) exists in this code path.

## Impact Explanation
`handleRequest` is the gateway's public HTTP entrypoint that also extracts a bearer JWT from the `Authorization` header and forwards the raw request to `ProcessRequest`: [3](#0-2) . If an operator configures a wildcard `CORSAllowedOrigins` entry (a documented, supported feature) and `CORSEnabled` is true, an attacker who registers/hosts a page on a lookalike domain sharing the suffix can have a victim's browser send a cross-origin request whose response the attacker's page can read, since the CORS response headers will incorrectly authorize it. This is a genuine allowlist-bypass / cross-origin response-exposure bug in gateway code, matching the CVE-2019-3788 bug class (unanchored wildcard-domain matching).

## Likelihood Explanation
Exploitation only requires (1) an operator using a wildcard CORS entry — a normal supported configuration, not a misuse of the feature — and (2) an attacker registering any domain ending in the same literal suffix, which is trivial, cheap, and requires no special privileges or access to the gateway/node. The vulnerable code path is unconditionally reachable by any unprivileged client via the `Origin` header on a normal HTTP request.

## Recommendation
Anchor the wildcard match to a real subdomain boundary, e.g. compare against `"."+allowedHost` (keeping the leading dot from the wildcard stripping) instead of the bare suffix:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```

## Proof of Concept
1. Configure `CORSEnabled = true`, `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request to the gateway HTTP path with header `Origin: https://evilethereum.org`.
3. `splitURL` yields `originHost = "evilethereum.org"`; wildcard stripping yields `allowedHost = "ethereum.org"`; `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.
4. Response includes `Access-Control-Allow-Origin: https://evilethereum.org`, verifiable with a unit test calling `isAllowedOrigin("https://evilethereum.org")` against config `CORSAllowedOrigins: []string{"https://*.ethereum.org"}` and asserting it returns `true` (unexpected/incorrect result).

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

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```
