### Title
CORS wildcard-origin allowlist bypass via suffix matching in the Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's user-facing HTTP server implements a custom `Origin` header check (`isAllowedOrigin`) that supports wildcard entries such as `https://*.remix.ethereum.org` in `CORSAllowedOrigins`. The wildcard match strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` with no boundary check, so any attacker-controlled domain that merely ends with the same characters as the allowlisted suffix (not just a genuine subdomain) will pass the check. This is directly analogous to the CVE's "bypass Same Origin Policy ... via crafted web site" bug class, except here it's the Gateway's own reimplementation of an origin allowlist that fails to enforce a real domain boundary.

### Finding Description
`isAllowedOrigin` in [1](#0-0)  parses both the request `Origin` header and each configured allowed origin via `splitURL`, then for a wildcard entry does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
`strings.HasSuffix` has no notion of a label/dot boundary. If the operator configures `CORSAllowedOrigins = ["https://*.remix.ethereum.org"]`, the code turns this into a bare suffix check against `remix.ethereum.org`. An origin such as `https://evil-remix.ethereum.org` (with no separating dot) satisfies `HasSuffix("evil-remix.ethereum.org", "remix.ethereum.org")` and is treated as allowed even though it is not a subdomain of the intended domain at all — it is an entirely different, attacker-registrable domain.

This is called from `handleRequest` at [2](#0-1) , which reflects the attacker's `Origin` value back in `Access-Control-Allow-Origin` when `isAllowedOrigin` returns true, letting a browser page hosted on the attacker's crafted domain read cross-origin responses from the Gateway's `/user` endpoint.

The existing unit tests only validate proper subdomain suffixes (e.g. `remix.ethereum.org` vs `another.valid.domain.com`) and never test an attacker domain that merely shares the tail characters without a dot boundary (e.g. `evil-ethereum.org` against `*.ethereum.org`), so this gap is not caught by [3](#0-2) .

### Impact Explanation
This affects the Gateway's `UserServerConfig` HTTP endpoint, which is the internet-facing entry point unprivileged clients (including browser-based dApps like Remix) use to submit JSON-RPC requests (e.g., vault secret operations, workflow triggers) as seen wired in [4](#0-3) . If an operator configures a wildcard allowlist entry intending to scope access to a specific domain and its subdomains, an attacker can register a look-alike domain that satisfies the flawed suffix check and get their page's cross-origin `fetch` requests treated as if they originated from the trusted origin. Combined with any Gateway response containing sensitive data or bearer-token-authenticated actions initiated by a tricked user's browser, this can lead to cross-origin request/response confusion analogous to the SOP-bypass class in the reported CVE. The severity is bounded by the fact that the Gateway does not use cookies for auth (JWT is via `Authorization: Bearer`, set in [5](#0-4) ) and no `Access-Control-Allow-Credentials` header is emitted, so credentialed-cookie exfiltration is not directly enabled — but any endpoint whose authorization decision is anchored to Origin, or any unauthenticated/public GET-style response, is exposed to unintended cross-origin read access.

### Likelihood Explanation
Exploitability depends entirely on an operator using a wildcard entry in `CORSAllowedOrigins` (a documented, supported feature per [6](#0-5) ) and CORS being enabled (`CORSEnabled = true`). This is a real, supported configuration pattern (the default sample config ships with CORS disabled, per [7](#0-6) , but production Gateway deployments serving browser dApps are expected to enable CORS with an allowlist). Registering a domain that satisfies the flawed suffix match (e.g. purchasing `evil<allowed-suffix>` or `<label>-<allowed-suffix>` without a dot) is trivial and requires no privileged access — matching the CVSS `AC:L/PR:N/UI:R` profile of the source CVE (a user must visit the attacker's crafted page).

### Recommendation
Fix the wildcard comparison to enforce a proper label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
i.e., require the matched suffix to be preceded by a literal `.` (or be an exact match of the base domain), not just any substring suffix. Add regression tests asserting that domains like `evil-ethereum.org` or `notethereum.org` are rejected against an `*.ethereum.org` allowlist entry.

### Proof of Concept
1. Operator configures the Gateway `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers `https://evil-ethereum.org` (or any domain ending in the literal characters `ethereum.org` without a separating dot) and hosts a page there.
3. Victim's browser visits the attacker page; the page's JavaScript issues a `fetch` to the Gateway's `/user` endpoint with `Origin: https://evil-ethereum.org`.
4. `isAllowedOrigin` computes `originHost = "evil-ethereum.org"`, `allowedHost = "ethereum.org"` (after stripping `*.`), and `strings.HasSuffix("evil-ethereum.org", "ethereum.org")` returns `true`, so the Gateway responds with `Access-Control-Allow-Origin: https://evil-ethereum.org`, granting the attacker page browser-level cross-origin access it should not have — reproducing the same bug class as the CVE's Same-Origin-Policy bypass, but rooted in this custom origin-allowlist logic rather than WebKit.

### Citations

**File:** core/services/gateway/network/httpserver.go (L33-35)
```go
type HTTPRequestHandler interface {
	ProcessRequest(ctx context.Context, rawMessage []byte, auth string) (rawResponse []byte, httpStatusCode int)
}
```

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

**File:** core/services/gateway/network/httpserver.go (L226-231)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}
```

**File:** core/services/gateway/network/httpserver_test.go (L152-186)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://*.gov"})

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin := "https://remix.ethereum.org"
	resp, respBytes := sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "https://another.valid.domain.com"
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "http://example.gov"
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Equal(t, origin, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Equal(t, "GET, POST, OPTIONS", resp.Header.Get("Access-Control-Allow-Methods"))
	require.Equal(t, "Content-Type", resp.Header.Get("Access-Control-Allow-Headers"))
}
```

**File:** core/scripts/gateway/sample_config.toml (L1-10)
```text
[UserServerConfig]
Port = 8080
Path = "/user"
ContentTypeHeader = "application/jsonrpc"
ReadTimeoutMillis = 1000
WriteTimeoutMillis = 1000
RequestTimeoutMillis = 1000
MaxRequestBytes = 10_000
CORSEnabled = false
CORSAllowedOrigins = []
```
