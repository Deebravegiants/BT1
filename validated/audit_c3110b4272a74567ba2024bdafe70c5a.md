### Title
CORS wildcard-origin allowlist bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's HTTP server validates `Origin` headers against a configured `CORSAllowedOrigins` list to decide whether to reflect `Access-Control-Allow-Origin`. The wildcard-subdomain match uses an unanchored `strings.HasSuffix` check, so any attacker-controlled hostname that merely ends with the allowed suffix (not just a proper subdomain) is treated as trusted.

### Finding Description
`isAllowedOrigin` splits the request `Origin` and each configured allowed origin into scheme/host/port and, for wildcard entries (`*.example.com`), strips the `*.` prefix and checks `strings.HasSuffix(originHost, allowedHost)`: [1](#0-0) 

This suffix check has no boundary/dot enforcement. Given an allowlist entry `*.remix.com`, `allowedHost` becomes `remix.com`, and `strings.HasSuffix("evilremix.com", "remix.com")` evaluates to `true` — even though `evilremix.com` is not a subdomain of `remix.com` at all, just a hostname that happens to share the suffix string. Any domain an unprivileged attacker can register/control that ends in the configured suffix (e.g. `notremix.com`, `attacker-remix.com`) will be treated as an allowed origin.

The result is then reflected verbatim into the response header in `handleRequest`: [2](#0-1) 

This is the internet-facing Gateway HTTP server that receives requests directly from unprivileged clients/browsers (`ProcessRequest` is invoked with the raw request body and any `Authorization: Bearer` JWT) [3](#0-2) , so this is a reachable, unprivileged-actor-facing surface, not an operator-only or mocked-only path.

### Impact Explanation
This is directly analogous to the CVE's root cause: improper/insufficiently anchored validation of an origin/URL string leads to a trust decision that a malicious actor can spoof. Here, instead of address-bar spoofing, it is CORS-origin spoofing: a page hosted on an attacker-controlled domain that shares a suffix with a trusted wildcard entry gets treated by the Gateway as an authorized cross-origin caller, and the Gateway reflects `Access-Control-Allow-Origin` back to that attacker origin. Any browser script running on such an attacker domain can then issue cross-origin requests to the Gateway and read the JSON-RPC responses that would otherwise be restricted to the legitimate `*.remix.com`-family origins — a cross-origin/cross-user response confusion. The severity depends on what sensitive data/actions the Gateway's HTTP path exposes to callers, and on whether any credentials (e.g., a bearer token embedded in a legitimate frontend running the same browser session) are attached by client code to such requests — this exploitation prerequisite could not be fully confirmed from the indexed files alone.

### Likelihood Explanation
Exploitation requires: (1) the operator configuring `CORSEnabled = true` with a wildcard entry in `CORSAllowedOrigins` (a supported and documented configuration, per `core/scripts/gateway/sample_config.toml`), and (2) an attacker registering/controlling a domain that string-suffix-matches the configured wildcard suffix (e.g., attacker buys `evilremix.com` when the allowlist has `*.remix.com`). This is a plausible, low-cost attack for an unprivileged external actor and needs no compromise of any Chainlink component — only a suitably-named domain.

### Recommendation
Change the wildcard match to enforce a proper subdomain boundary, e.g. verify `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`, so `evilremix.com` no longer satisfies `*.remix.com`. Add unit tests covering non-subdomain suffix collisions (`evilremix.com`, `notremix.com`, `xremix.com`) to prevent regression.

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.remix.com"]`.
2. From an attacker-controlled site `https://evilremix.com`, send a browser `fetch`/XHR request to the Gateway's configured `Path` endpoint with header `Origin: https://evilremix.com`.
3. `isAllowedOrigin` computes `allowedHost = "remix.com"` and evaluates `strings.HasSuffix("evilremix.com", "remix.com")` → `true`, so the Gateway responds with `Access-Control-Allow-Origin: https://evilremix.com`, allowing the attacker page's script to read the JSON-RPC response body cross-origin. [4](#0-3)

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-202)
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
