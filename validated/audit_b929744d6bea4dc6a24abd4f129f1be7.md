The code exactly matches the claim, and this vulnerability class (allowlist bypass via unbounded string suffix match) is not excluded by `SECURITY.md`. The claim is verified as accurate against the actual source.

Audit Report

## Title
CORS `Access-Control-Allow-Origin` allowlist bypass via unanchored suffix match in `isAllowedOrigin` - ([File: core/services/gateway/network/httpserver.go])

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements wildcard CORS origin matching with a raw `strings.HasSuffix(originHost, allowedHost)` check after stripping the `*.` prefix, with no domain-label boundary enforcement. This lets an attacker-controlled domain that merely ends with the configured suffix (e.g. `evilremix.com` against an allowlisted `*.remix.com`) pass the check and receive a reflected `Access-Control-Allow-Origin` header, even though it is not a genuine subdomain.

## Finding Description
The wildcard branch of `isAllowedOrigin` strips the literal `*.` from a configured allowed origin (e.g. `*.remix.com` → `remix.com`) and then does a plain suffix comparison: [1](#0-0) . This is a plain string suffix test with no check that the character preceding the matched suffix is a `.` (or any other structural label boundary), so any origin host ending in the literal characters `remix.com` — such as `evilremix.com`, `attacker-remix.com`, or `notremix.com` — satisfies `strings.HasSuffix`, even though none of these are subdomains of `remix.com`. The exact-match branch above it is fine [2](#0-1) , but the wildcard branch's boundary check is broken.

This function is invoked directly from `handleRequest`, the entry point for every HTTP request hitting the Gateway's internet-facing server, before any authentication/JWT extraction takes place: [3](#0-2) . There is no other validation layer between the raw `Origin` header and the CORS header reflection — no separator-aware allowlist check exists anywhere else in this file.

## Impact Explanation
This gates the `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers` response headers on the Gateway's unauthenticated HTTP front door. If an operator configures a wildcard allowlist entry such as `*.remix.com`, an attacker who registers a domain like `evilremix.com` can send a cross-origin browser request with `Origin: https://evilremix.com` and receive that value reflected back in `Access-Control-Allow-Origin`, allowing a page hosted on the attacker's domain to read Gateway JSON-RPC responses cross-origin via `fetch()`/XHR that were intended only for genuine subdomains of the trusted partner domain. This is a concrete allowlist bypass in an internet-facing gateway component, matching the in-scope "allowlist ... bypass" impact category.

## Likelihood Explanation
Exploitation requires an operator to have configured a wildcard CORS entry — a documented, supported configuration option (`CORSAllowedOrigins`), not a misconfiguration or privileged action by the attacker. Once such a config is known or guessed (e.g., publicly known partner domain), an unprivileged attacker can cheaply register a lookalike domain sharing the suffix and repeatably exploit the bypass with no credentials, host access, or victim social engineering required beyond standard cross-origin browser requests.

## Recommendation
Enforce a proper label boundary in the wildcard match: after stripping `*.`, require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` so only genuine subdomains (`foo.remix.com`) match, rejecting domains that merely share a string suffix (`evilremix.com`).

## Proof of Concept
Configure `CORSAllowedOrigins = []string{"https://*.remix.com"}` and send an HTTP request to the Gateway with header `Origin: https://evilremix.com`. `isAllowedOrigin` splits the origin to host `evilremix.com`, strips `*.` from the allowed entry to get `remix.com`, and `strings.HasSuffix("evilremix.com", "remix.com")` returns `true` [4](#0-3) , causing `handleRequest` to set `Access-Control-Allow-Origin: https://evilremix.com` in the response [5](#0-4) . A Go unit test calling `isAllowedOrigin("https://evilremix.com")` with the above config and asserting it returns `true` (when it should return `false`) directly proves the bypass.

### Citations

**File:** core/services/gateway/network/httpserver.go (L180-183)
```go
		// check for exact host match (e.g., remix.com)
		if originHost == allowedHost {
			return true
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
