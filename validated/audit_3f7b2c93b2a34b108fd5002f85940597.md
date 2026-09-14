Confirmed. This is a direct analog of the Deno bug: `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` strips the `*.` prefix from a configured allowed origin and then performs a raw `strings.HasSuffix(originHost, allowedHost)` check with no dot-boundary enforcement, so a hostname that merely ends with the same characters (not a proper subdomain) will be treated as allowed.

### Title
CORS wildcard origin allowlist bypass via improper suffix matching (missing dot-boundary check) - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's internet-facing HTTP server validates the `Origin` header against a configured `CORSAllowedOrigins` list. For wildcard entries (`*.example.com`), it strips the `*.` and checks `strings.HasSuffix(originHost, allowedHost)` [1](#0-0) . This is the same bug class as CVE-2024-27932: a raw suffix check without verifying a dot (or exact) boundary lets `evilethereum.org` (or `attacker-ethereum.org`) satisfy an allowlist entry meant only for `*.ethereum.org`, since it also "ends with" `ethereum.org`.

### Finding Description
`isAllowedOrigin` parses the incoming request's `Origin` header and each configured allowed origin via `splitURL`, which lowercases and extracts scheme/host/port [2](#0-1) . For entries starting with `*.`, it trims the wildcard prefix and does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [1](#0-0) 
Because `strings.HasSuffix` only checks that `originHost` ends with the literal characters of `allowedHost`, an attacker-controlled domain such as `evil-ethereum.org` or `notethereum.org` (registered by the attacker) will match an allowlist entry of `*.ethereum.org`, since it "ends with" `ethereum.org` even though it is not actually a subdomain of `ethereum.org`. A proper implementation would require the origin to equal `allowedHost` or end with `"."+allowedHost`.

This directly mirrors the reported Deno flaw where `ends_with` matching on hostnames caused a token scoped to `deno.land` to also match `im-in-ur-servers-attacking-ur-deno.land`.

### Impact Explanation
If `isAllowedOrigin` returns true, the handler reflects the attacker's `Origin` back in `Access-Control-Allow-Origin` [3](#0-2) , permitting a page hosted on the attacker's spoofed domain to make cross-origin credentialed/browser requests to the Gateway's HTTP endpoint that should only be reachable from trusted first-party subdomains. This is a concrete allowlist-bypass allowing unauthorized cross-origin access from an unprivileged web client to the gateway-facing API, which processes `ProcessRequest` calls including bearer-token-authenticated requests [4](#0-3) .

### Likelihood Explanation
Exploitation only requires registering a domain that happens to end with the same suffix as a configured wildcard allowlist entry (e.g., `evil-ethereum.org` for an entry of `*.ethereum.org`) and hosting a malicious page there that issues a cross-origin request against the Gateway. No privileged access or network position is required — this is purely a client-side/browser-based bypass reachable by any unprivileged actor once operators configure a wildcard CORS entry, which is an intended supported feature [5](#0-4) .

### Recommendation
Replace the raw `strings.HasSuffix` check with a boundary-aware comparison, e.g. require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`, ensuring the matched suffix begins immediately after a dot separator so arbitrary same-suffix domains cannot be conflated with true subdomains.

### Proof of Concept
1. Configure the gateway with `CORSAllowedOrigins: ["https://*.ethereum.org"]`.
2. From an unprivileged browser context, send a cross-origin request to the gateway's HTTP path with header `Origin: https://evil-ethereum.org` (a domain registered by the attacker).
3. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and checks `strings.HasSuffix("evil-ethereum.org", "ethereum.org")`, which evaluates to `true` [1](#0-0) .
4. The server responds with `Access-Control-Allow-Origin: https://evil-ethereum.org`, granting the attacker's page CORS access it should not have.

### Citations

**File:** core/services/gateway/network/httpserver.go (L138-155)
```go
func (s *httpServer) splitURL(rawURL string) (string, string, string, error) {
	// lowercase the URL to avoid case sensitivity issues
	parsedURL, err := url.Parse(strings.ToLower(rawURL))
	if err != nil {
		return "", "", "", fmt.Errorf("error parsing URL: %w", err)
	}

	host, port, err := net.SplitHostPort(parsedURL.Host)
	if err != nil {
		// if there's no port, the host itself is returned
		if parsedURL.Host != "" {
			return parsedURL.Scheme, parsedURL.Host, "", nil
		}
		return "", "", "", fmt.Errorf("error splitting host and port: %w", err)
	}

	return parsedURL.Scheme, host, port, nil
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

**File:** core/services/gateway/network/httpserver.go (L195-202)
```go
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

**File:** core/services/gateway/network/httpserver_test.go (L152-155)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://*.gov"})
```
