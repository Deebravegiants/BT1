I found a suitable analog: a wildcard-origin CORS allowlist check in the gateway's HTTP server that performs an unanchored suffix match, letting an attacker-registered domain like `evilremix.com` satisfy a `*.remix.com` allow-rule.I have enough evidence to finalize the finding. The vulnerable logic is in `isAllowedOrigin` in `core/services/gateway/network/httpserver.go`, invoked by `handleRequest` on every unauthenticated HTTP request to the gateway's internet-facing HTTP endpoint.

### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway HTTP server's CORS origin allowlist supports wildcard entries like `*.remix.com`, but the wildcard match is implemented as a raw `strings.HasSuffix` check on the hostname with no delimiter/boundary validation. This allows an attacker who controls (or registers) a domain that merely *ends with* the allowed suffix — e.g. `evilremix.com` for an allowed pattern `*.remix.com` — to have their `Origin` header accepted as a legitimate subdomain, bypassing the intended CORS restriction. This mirrors the CVE's bug class: a security-relevant name/domain comparison implemented with an insufficiently strict string-matching primitive, causing a request that should be rejected to be accepted.

### Finding Description
`isAllowedOrigin` splits both the incoming request's `Origin` header and each configured allowed-origin entry into scheme/host/port via `splitURL`, then compares them: [1](#0-0) 

Specifically, for wildcard entries the code strips the leading `*.` and then does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
`strings.HasSuffix(originHost, allowedHost)` has no boundary check requiring a `.` immediately before the matched suffix. Consequently, given an allowed pattern `*.remix.com`, `allowedHost` becomes `"remix.com"`, and any `originHost` ending in the literal characters `remix.com` — including `evilremix.com`, `notremix.com`, or `attacker-remix.com` — satisfies the suffix check and is treated as an authorized subdomain of `remix.com`, even though it is an entirely different, attacker-controlled domain.

This check is reached directly from `handleRequest`, which is wired to every incoming HTTP request on the gateway's public listener: [2](#0-1) 

No authentication is required to trigger this path — any unprivileged client can send an HTTP request with a crafted `Origin` header.

### Impact Explanation
If `CORSEnabled` is true and an operator configures a wildcard allowlist entry (e.g. `*.remix.com`, as used in the project's own test fixtures), an attacker-controlled origin domain sharing only a string suffix with the allowed domain (not a genuine subdomain) will receive `Access-Control-Allow-Origin` reflecting their origin plus `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`. This lets a malicious website hosted on such a domain perform authenticated-looking cross-origin requests against the gateway from a victim's browser, exceeding the operator's intended trust boundary. The severity depends on what the gateway's HTTP endpoint exposes (it forwards to `HTTPRequestHandler.ProcessRequest`, which can include JWT/bearer-token-authenticated flows) — this raises cross-origin request risk against a browser-facing endpoint, but does not itself leak secrets or bypass the underlying request-level authentication (e.g. `Authorization: Bearer` JWT checks) that the handler performs. It is best characterized as an allowlist bypass in the CORS layer of the internet-facing gateway.

### Likelihood Explanation
Likelihood depends on: (1) `CORSEnabled=true` in the deployment, and (2) at least one wildcard origin (`*.<domain>`) being configured — both of which are supported, documented configuration options and appear in this repo's own test suite (`httpserver_test.go`, `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` uses `*.ethereum.org`, `*.valid.domain.com`). Any attacker only needs to register/control a domain with the matching suffix string and send a crafted request — no privileged access or network-layer capability is required.

### Recommendation
Change the wildcard-suffix comparison to enforce a proper subdomain boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This ensures `evilremix.com` no longer satisfies `*.remix.com`, while genuine subdomains like `api.remix.com` still match.

### Proof of Concept
1. Configure the gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. Send an HTTP request to the gateway's configured `Path` with header `Origin: https://evilremix.com`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilremix.com`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, even though `evilremix.com` is not a subdomain of `remix.com`. [3](#0-2)

### Citations

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
