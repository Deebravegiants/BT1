Audit Report

## Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway HTTP server's `isAllowedOrigin` function implements wildcard CORS matching (e.g. `*.remix.com`) using an unbounded `strings.HasSuffix` comparison instead of checking for a proper subdomain delimiter. This allows an attacker who registers a domain that merely ends with the same characters as the allowed suffix (e.g. `evilremix.com` for allow-rule `*.remix.com`) to have their `Origin` accepted as if it were a legitimate subdomain, causing the gateway to emit permissive CORS headers for that unrelated, attacker-controlled origin.

## Finding Description
In `core/services/gateway/network/httpserver.go`, `isAllowedOrigin` parses the incoming `Origin` header and each configured `CORSAllowedOrigins` entry via `splitURL`, matching scheme and port exactly, then handling host matching. For wildcard entries it strips the `*.` prefix and does a raw suffix check with no boundary/delimiter validation: [1](#0-0) 

Because `strings.HasSuffix(originHost, allowedHost)` treats `allowedHost` as a literal string suffix rather than a domain label boundary, `originHost = "evilremix.com"` satisfies `allowedHost = "remix.com"` even though `evilremix.com` is not `remix.com` or any subdomain of it. This function is called unconditionally from `handleRequest`, the handler wired to every request on the gateway's public HTTP path, whenever `CORSEnabled` is true: [2](#0-1) 

No authentication precedes this check — any client can set an arbitrary `Origin` header. There is no existing boundary check (e.g. requiring a preceding `.`) that would prevent this bypass.

## Impact Explanation
When an operator enables `CORSEnabled` and configures a wildcard entry such as `*.remix.com` (a documented, supported feature exercised in this repo's own test suite), an attacker controlling any domain that string-ends-with `remix.com` (`evilremix.com`, `notremix.com`, etc.) can have the gateway reflect `Access-Control-Allow-Origin` for their domain and set permissive `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`. This breaks the intended CORS allowlist boundary and lets a malicious site perform cross-origin requests against the gateway's HTTP endpoint that the operator explicitly intended to restrict to genuine subdomains of the trusted domain — an allowlist-bypass class issue in the gateway's browser-facing HTTP layer. It does not itself defeat request-level authentication (e.g. bearer/JWT checks in `ProcessRequest`), so the practical impact is scoped to the CORS trust boundary rather than a full authentication bypass.

## Likelihood Explanation
Exploitation requires only that the operator enable CORS and use a wildcard allow-entry — both normal, supported configuration choices, not insecure defaults or operator error being exploited by an insider. Given that precondition, any unprivileged external attacker can register a domain with the matching suffix and send a request with a crafted `Origin` header; this is trivially repeatable and requires no credentials, elevated role, or network-level capability.

## Recommendation
Enforce a proper subdomain boundary in the wildcard branch, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This rejects `evilremix.com` while still matching genuine subdomains like `api.remix.com`.

## Proof of Concept
1. Start the gateway HTTP server with `CORSEnabled: true` and `CORSAllowedOrigins: ["https://*.remix.com"]`.
2. Send `GET`/`OPTIONS` to the configured `Path` with header `Origin: https://evilremix.com`.
3. Observe the response contains `Access-Control-Allow-Origin: https://evilremix.com` (and CORS method/header allowances), confirming the suffix-based allowlist accepted a non-subdomain, attacker-controlled origin — this can be codified as a Go unit test analogous to the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` in `httpserver_test.go`, asserting `isAllowedOrigin("https://evilremix.com")` returns `true` for allow-list `*.remix.com`.

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
