Audit Report

## Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway's `isAllowedOrigin` function matches wildcard-domain allowlist entries (e.g. `*.remix.com`) using an unanchored `strings.HasSuffix` comparison instead of requiring a subdomain boundary (`.`) before the allowed suffix. As a result, an attacker-controlled domain such as `evilremix.com` is incorrectly treated as a subdomain of `remix.com` and passes the CORS allowlist check.

## Finding Description
`isAllowedOrigin` parses the request's `Origin` header and, for wildcard-prefixed allowlist entries, strips the `*.` and checks `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

This check does not verify that a literal `.` (or exact host-length match) precedes the suffix, so any origin host that merely ends with the configured suffix string — not just true subdomains — satisfies the check. For an allowlist entry `https://*.remix.com`, `allowedHost` becomes `remix.com`, and `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`, incorrectly matching an unrelated domain.

This function directly gates whether `handleRequest` echoes `Access-Control-Allow-Origin` for the caller-supplied `Origin` header: [2](#0-1) 

No other authentication, redaction, or validation logic intervenes between the origin check and the CORS header being set — the flawed suffix check is the sole gate. Any unprivileged remote client can send a request with a crafted `Origin` header to this internet-facing endpoint.

## Impact Explanation
If an operator configures a wildcard CORS allowlist entry (e.g. `*.remix.com`), a completely unrelated attacker-registered domain like `evilremix.com` is treated as an allowed origin, causing the gateway to echo back `Access-Control-Allow-Origin` for that domain. This is a concrete allowlist-bypass in the gateway's CORS handling, potentially enabling cross-origin browser requests from an attacker-controlled site to read gateway responses in a victim's browser session — mapping to the in-scope "allowlist bypass" / "cross-user response corruption" impact category for the gateway.

## Likelihood Explanation
Exploitation requires only that the operator has configured a wildcard CORS entry (a supported, intended feature of this code) and that an attacker registers a domain string ending in the allowed suffix — no privileged access, credentials, or node/peer compromise is needed. This is a client-side attack triggerable purely via a crafted `Origin` header, which any unprivileged actor can send.

## Recommendation
Anchor the wildcard match on a domain boundary, e.g. check that `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)`, rather than a raw string suffix, to ensure only genuine subdomains of the allowed base domain match.

## Proof of Concept
1. Configure the gateway with `CORSAllowedOrigins = ["https://*.remix.com"]` and `CORSEnabled = true`.
2. Send an HTTP request to the gateway's configured `Path` endpoint with header `Origin: https://evilremix.com`.
3. `isAllowedOrigin` computes `allowedHost = "remix.com"`, `originHost = "evilremix.com"`, and `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`.
4. The response includes `Access-Control-Allow-Origin: https://evilremix.com`, incorrectly granting CORS access to the attacker's domain. This can be verified with a Go unit test directly calling `httpServer.isAllowedOrigin("https://evilremix.com")` against a config with `CORSAllowedOrigins: []string{"https://*.remix.com"}` and asserting it returns `true`.

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

**File:** core/services/gateway/network/httpserver.go (L196-202)
```go
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}
```
