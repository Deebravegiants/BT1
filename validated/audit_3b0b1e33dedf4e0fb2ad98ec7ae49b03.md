Audit Report

## Title
CORS wildcard allowlist bypass via unanchored suffix match in `isAllowedOrigin` allows attacker-registered domains to pass subdomain validation - (File: core/services/gateway/network/httpserver.go)

## Summary
The gateway's `isAllowedOrigin` function, used to validate `Origin` headers against the operator-configured `CORSAllowedOrigins` wildcard list, performs a raw `strings.HasSuffix` comparison without enforcing a label/dot boundary. An operator who configures `*.example.com` intending to permit only subdomains of `example.com` will also inadvertently accept any domain that merely ends with that string, such as `evilexample.com`.

## Finding Description
In [1](#0-0) , the wildcard branch strips the `*.` prefix from the configured host and then checks `strings.HasSuffix(originHost, allowedHost)`. This is a plain suffix match: it does not verify that the character immediately preceding `allowedHost` in `originHost` is a `.`, so `evilethereum.org` satisfies `HasSuffix("evilethereum.org", "ethereum.org")` just as `foo.ethereum.org` does. The scheme and port checks preceding this in the same function [2](#0-1)  do not mitigate this because they only compare scheme/port equality, not host structure. When `isAllowedOrigin` returns true, `handleRequest` reflects the attacker's exact `Origin` into `Access-Control-Allow-Origin` [3](#0-2) , letting a browser at the attacker-controlled origin read cross-origin responses from the gateway's `/user` (or configured) JSON-RPC endpoint.

## Impact Explanation
This is a genuine implementation flaw in origin validation on the gateway's internet-facing endpoint (`UserServerConfig`), falling into the allowlist-bypass / cross-origin response exposure impact class. It undermines the operator's explicit intent when they configure a wildcard allowlist — the code fails to honor a properly-scoped configuration, which is a code bug rather than an operator misconfiguration. The confirmed root cause is the missing dot-boundary check.

## Likelihood Explanation
Exploitation requires: (1) an operator has enabled `CORSEnabled` with a wildcard entry in `CORSAllowedOrigins` — a supported, documented configuration option, not a hardening failure; and (2) an attacker registers/controls a domain with a matching suffix (unprivileged, low-cost) and gets a victim's browser to visit it while that browser can present valid gateway credentials. However, gateway authentication in `handleRequest` uses an explicit `Authorization: Bearer` header extracted from the request [4](#0-3)  rather than a cookie/session automatically attached by the browser. Browsers do not automatically forward a JWT that JavaScript on the attacker's origin does not already possess — same-origin policy prevents the attacker's script from reading tokens stored under the gateway's or a legitimate client's origin. Without an ambient credential the browser auto-attaches (as with cookies), the CORS bypass alone does not grant the attacker a working authenticated session token; the attacker would already need the victim's JWT through some other means, at which point they could call the gateway directly without needing a CORS bypass at all. This materially undercuts the "read authenticated vault/workflow responses" impact scenario in the PoC, which assumes the attacker's page already has the bearer token.

## Recommendation
Independent of the above caveat, the suffix-match logic is still incorrect and should be fixed to require a `.` boundary (or exact equality) before the allowed suffix, and negative test cases (e.g., `evilethereum.org`) should be added to `httpserver_test.go` to prevent silent host-confusion in the wildcard matcher, since it is a real code defect even though the JWT-based auth model limits practical session-hijacking impact via ambient credentials.

## Proof of Concept
Unit test target: `TestHTTPServer_isAllowedOrigin` in `core/services/gateway/network/httpserver_test.go` — configure `CORSAllowedOrigins = ["https://*.ethereum.org"]` and assert `isAllowedOrigin("https://evilethereum.org")` returns `true` (demonstrating the bypass), then verify the returned `Access-Control-Allow-Origin` header reflects `https://evilethereum.org` in `handleRequest`. Note: for full exploit chain to unauthenticated/authenticated data exposure, an accompanying analysis of how JWTs reach the browser client (whether via cookie, localStorage on the trusted origin, or manual header-setting) is needed to establish that ambient/automatically-forwarded credentials exist; the current PoC assumes the attacker already possesses the bearer token, which is not established by this code path alone.

### Citations

**File:** core/services/gateway/network/httpserver.go (L172-179)
```go
		// skip if the scheme doesn't match at all
		if originScheme != allowedScheme {
			continue
		}
		// skip if the port doesn't match at all
		if originPort != allowedPort {
			continue
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

**File:** core/services/gateway/network/httpserver.go (L226-231)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}
```
