## Analysis Result [1](#0-0) 

The strongest analog to CURL-CVE-2014-3613 (domain-suffix confusion due to missing boundary checks) is in the gateway's CORS origin validation, `isAllowedOrigin`.

### Title
CORS wildcard-origin bypass via unanchored suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
`isAllowedOrigin` validates the `Origin` header against `CORSAllowedOrigins` entries. For wildcard entries (`*.example.com`), it strips the `*.` prefix and performs a plain `strings.HasSuffix(originHost, allowedHost)` check with no boundary/dot separator enforcement, exactly mirroring the curl cookie-domain bug where a bare suffix match (`.168.0.1`) let `129.168.0.1` be treated as matching `192.168.0.1`.

### Finding Description [2](#0-1) 

```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```

If an operator configures `CORSAllowedOrigins` with an entry such as `https://*.remix.com`, `allowedHost` becomes `remix.com`. The check `strings.HasSuffix(originHost, "remix.com")` will also match hostile hosts such as `evilremix.com`, `notremix.com`, or any domain the attacker registers ending in that literal substring — there is no requirement that a `.` immediately precede the allowed suffix. This is the same missing-boundary root cause as the referenced CVE: a substring/suffix match is used where a label-boundary match (`strings.HasSuffix(originHost, "."+allowedHost)`, or `originHost == allowedHost`) is required.

This check gates the gateway's internet-facing HTTP server used for `handleRequest`, which processes JSON-RPC messages and returns `rawResponse` from `s.handler.ProcessRequest`: [3](#0-2) 

### Impact Explanation
When `CORSEnabled` is true and the forged `Origin` passes `isAllowedOrigin`, the server echoes it back in `Access-Control-Allow-Origin`, which permits a browser running attacker-controlled JavaScript on `evilremix.com` to read cross-origin fetch() responses from the gateway endpoint that would otherwise be restricted to the legitimately allowlisted `*.remix.com` origin. Depending on deployment, this endpoint routes gateway JSON-RPC handlers (e.g. capability/trigger/vault handlers) whose responses could include job/workflow data not intended for arbitrary third-party sites, enabling cross-user response confusion / unauthorized read of gateway responses by an unprivileged, purely client-side attacker (no node or peer compromise required).

### Likelihood Explanation
Exploitation requires only that: (1) the gateway operator has `CORSEnabled=true` with a wildcard entry in `CORSAllowedOrigins` (a documented supported pattern, `*.domain.com`), and (2) an attacker registers/controls any domain literally ending in that suffix (or a subdomain host they don't own but that shares the tail string, e.g. `attacker-remix.com`). This is a low-effort, purely client-side (browser) attack with no special privileges — matching the "unprivileged actor" scope.

### Recommendation
Anchor the wildcard suffix match to a label boundary, e.g.:
```go
if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
    return true
}
```
This ensures `evilremix.com` no longer matches `*.remix.com`, while `sub.remix.com` still does.

### Proof of Concept
1. Configure gateway with `CORSEnabled=true` and `CORSAllowedOrigins=["https://*.remix.com"]`.
2. From a browser on `https://evilremix.com`, send a fetch/XHR request to the gateway HTTP endpoint with `Origin: https://evilremix.com`.
3. `splitURL` yields `originHost="evilremix.com"`; the wildcard branch strips `allowedHost` to `remix.com`; `strings.HasSuffix("evilremix.com", "remix.com")` returns `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilremix.com`, and the browser allows `evilremix.com`'s script to read the response body, which is not the intent of the `*.remix.com` allowlist entry.

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
