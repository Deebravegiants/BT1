Audit Report

## Title
CORS wildcard-origin allowlist match uses unanchored suffix comparison, allowing domain spoofing of trusted origins - (File: `core/services/gateway/network/httpserver.go`)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` implements wildcard-origin matching for the gateway's CORS allowlist (e.g. `*.remix.com`). For wildcard entries, it strips the `*.` prefix and checks `strings.HasSuffix(originHost, allowedHost)` without requiring a `.` label boundary before the match, so any hostname that merely ends with the same character sequence (e.g. `evilremix.com`) is wrongly treated as a trusted subdomain of `remix.com`.

## Finding Description
The code at [1](#0-0)  strips the `*.` prefix from a configured wildcard entry and performs a plain string suffix comparison against the request's `Origin` header host, with no check that the preceding character is a `.` or that the hosts are otherwise properly delimited. This means `evilremix.com`, `notremix.com`, or `xremix.com` all satisfy `strings.HasSuffix(originHost, "remix.com")` even though none of them is a genuine subdomain of `remix.com`. The exact match branch (`originHost == allowedHost`) is safe, but the wildcard branch has no equivalent anchoring. This is reachable via `handleRequest`, which reflects the attacker-supplied `Origin` header back into `Access-Control-Allow-Origin` once `isAllowedOrigin` returns true, per [2](#0-1) . No authentication, prior privilege, or special network position is required — a browser or `curl` client can send an arbitrary `Origin` header to the internet-facing gateway HTTP endpoint.

## Impact Explanation
This is a concrete CORS allowlist bypass: a domain crafted to satisfy the flawed suffix check gains the same cross-origin read access as a legitimately allowlisted subdomain, allowing an attacker-hosted page to read gateway JSON-RPC responses intended only for explicitly trusted partner domains. This maps to the in-scope "allowlist bypass" / "gateway request impersonation" impact category.

## Likelihood Explanation
Exploitation only requires registering/hosting a domain ending in the same string as an allowlisted root domain and configuring `CORSEnabled: true` with a `*.<domain>` entry (a supported, documented configuration option, not a misconfiguration in itself since wildcard is an intended feature). No operator, admin, or host access is needed — any unprivileged web client can trigger the flawed check by sending a crafted `Origin` header.

## Recommendation
Anchor the suffix match to a label boundary or exact equality:
```go
if strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost {
    return true
}
```

## Proof of Concept
1. Configure gateway with `CORSEnabled: true`, `CORSAllowedOrigins: ["https://*.remix.com"]`.
2. Send a request to the gateway's configured HTTP path with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`, confirming the spoofed non-subdomain origin is granted trusted cross-origin access, per [3](#0-2) .

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
