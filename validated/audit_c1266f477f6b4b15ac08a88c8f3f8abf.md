The code matches the claim exactly - the current implementation confirms the vulnerability.

Audit Report

## Title
Wildcard CORS origin allowlist bypass via unbounded suffix match - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements wildcard CORS matching using a bare `strings.HasSuffix(originHost, allowedHost)` check after stripping the `*.` prefix, with no requirement for a `.` domain-label boundary. This lets any attacker-registered domain that merely ends with the same character sequence as an allowed suffix (e.g. `evilexample.com` matching `*.example.com`) pass the CORS allowlist check, even though it is not a genuine subdomain. [1](#0-0) 

## Finding Description
The `isAllowedOrigin` function parses the `Origin` header and each `CORSAllowedOrigins` entry via `splitURL`, then for wildcard entries starting with `*.`, strips the prefix and checks only `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

This is a pure string-suffix comparison with no verification that a `.` character (a domain-label boundary) separates the attacker-controlled prefix from the allowed suffix. As a result, `originHost = "evilexample.com"` satisfies `strings.HasSuffix("evilexample.com", "example.com")` even though `evilexample.com` is an entirely separate, attacker-registrable domain unrelated to `example.com`. The exact host match branch (`originHost == allowedHost`) is correct, but the wildcard branch that follows it lacks the equivalent boundary check. [2](#0-1) 

The result of `isAllowedOrigin` is used directly in `handleRequest` to reflect the attacker-supplied `Origin` value into the `Access-Control-Allow-Origin` response header: [3](#0-2) 

No other validation, redaction, or boundary check exists elsewhere in the file to compensate for this gap.

## Impact Explanation
This is a legitimate allowlist-bypass bug: when an operator configures `CORSAllowedOrigins` with a wildcard entry (e.g. `*.example.com`) intending to scope trust to genuine subdomains of a domain they control, an attacker who registers a look-alike domain (`evilexample.com`, `notexample.com`) can have a script hosted on that domain bypass the CORS check, causing the Gateway to set `Access-Control-Allow-Origin` to the attacker's origin. This lets the attacker's page make credentialed-equivalent cross-origin requests to the `/user` endpoint and read the JSON-RPC response, which maps to the in-scope "allowlist bypass" / "cross-user response corruption" impact categories on an internet-facing gateway component. [4](#0-3) 

## Likelihood Explanation
Exploitation requires only that (1) the operator has configured a wildcard entry in `CORSAllowedOrigins` (a supported, documented configuration pattern), and (2) the attacker registers a domain string ending with the allowed suffix and hosts a page issuing a cross-origin request with that `Origin` header — both fully within an unprivileged remote attacker's control with no compromise of the legitimate domain needed. This makes the bug reliably and repeatably triggerable whenever wildcard CORS is used.

## Recommendation
Fix the wildcard matching in `isAllowedOrigin` to require an explicit domain-label boundary — e.g., after stripping the `*.` prefix, check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of the bare `strings.HasSuffix` comparison. Consider using a vetted URL/host/domain-suffix comparison library to avoid similar boundary errors.

## Proof of Concept
1. Configure Gateway `HTTPServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = []string{"https://*.example.com"}`.
2. Send an HTTP request to the Gateway's configured path with header `Origin: https://evilexample.com`.
3. In `isAllowedOrigin`: `allowedHost` becomes `example.com` after stripping `*.`; `originHost` is `evilexample.com`. Since `strings.HasSuffix("evilexample.com", "example.com")` is `true`, the function returns `true`.
4. Observe the response contains `Access-Control-Allow-Origin: https://evilexample.com`, confirming the bypass. This can be codified as a Go unit test calling `isAllowedOrigin("https://evilexample.com")` directly against a server configured with `CORSAllowedOrigins: []string{"https://*.example.com"}` and asserting it returns `true` (expected: `false`).

### Citations

**File:** core/services/gateway/network/httpserver.go (L180-190)
```go
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
