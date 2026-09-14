Confirmed. This is the same bug class as the Mongoose advisory — a wildcard hostname match that doesn't validate label boundaries — reachable by any unauthenticated client sending a crafted `Origin` header to the internet-facing gateway HTTP server.

### Title
CORS wildcard-origin check uses unanchored suffix match, allowing origin spoofing via lookalike domains - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's `httpServer.isAllowedOrigin` implements wildcard CORS-origin matching (`*.example.com`) by stripping the `*.` prefix and then checking `strings.HasSuffix(originHost, allowedHost)`, with no check that the character preceding the suffix is a `.` (dot) label separator. Any hostname that merely ends with the configured suffix — including domains with no subdomain relationship at all, like `evilethereum.org` for a `*.ethereum.org` allowlist entry — is treated as an allowed CORS origin. This is analogous to the Mongoose `mg_match()` bug where wildcard patterns crossed DNS label boundaries.

### Finding Description
`isAllowedOrigin` [1](#0-0)  parses the incoming `Origin` header and each configured `CORSAllowedOrigins` entry via `splitURL`, then compares scheme, port, and host. For wildcard entries it does:

```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

There is no verification that the character immediately preceding the matched suffix in `originHost` is a `.`. Consequently, `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, so an attacker-controlled origin such as `https://evilethereum.org` (or `https://xethereum.org`, `https://notethereum.org`, etc.) is accepted for an allowlist entry `https://*.ethereum.org`, even though it is not a subdomain of `ethereum.org` at all.

`handleRequest` [3](#0-2)  calls this function and, on a match, echoes the attacker-supplied `Origin` back in `Access-Control-Allow-Origin`, enabling the browser to permit cross-origin reads of gateway responses from the spoofed origin.

Existing tests only exercise true subdomains/non-subdomains that don't share a suffix without a dot boundary (e.g. `ethereum.remix.org` vs `*.ethereum.org`) [4](#0-3) , so this boundary-less suffix match is not covered by the current test matrix.

### Impact Explanation
The Chainlink Gateway is an internet-facing component that brokers unprivileged client requests (e.g. workflow/capability API traffic) into the DON [3](#0-2) . If `CORSEnabled` is on and any allowlist entry uses the `*.` wildcard form, an attacker who registers a domain that merely ends with the configured suffix (no subdomain relationship required) can serve a malicious webpage that makes credentialed/cross-origin browser requests to the gateway and read the JSON-RPC responses, bypassing the intended CORS restriction — a cross-origin response confusion / access-control bypass.

### Likelihood Explanation
Exploitability requires: (1) the operator has `WebServer`/gateway `CORSEnabled=true` with at least one wildcard entry in `CORSAllowedOrigins`, and (2) the attacker registers or controls a domain sharing the wildcard's suffix without the dot boundary (cheap and easy — attacker fully controls domain registration, e.g. `evil-ethereum.org` vs. allowlisted `*.ethereum.org`). No privileged access or network position is required — a normal unauthenticated web client triggers it purely via the `Origin` header.

### Recommendation
Require the label boundary when doing suffix matching: after stripping `*.`, check that `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `HasSuffix`.

### Proof of Concept
1. Configure gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers `evilethereum.org` and serves a page there.
3. Browser on that page sends `fetch(gatewayURL, {headers: {Origin: "https://evilethereum.org"}})`.
4. `isAllowedOrigin("https://evilethereum.org")` strips wildcard to `ethereum.org`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, so the gateway responds with `Access-Control-Allow-Origin: https://evilethereum.org` [5](#0-4) , letting the attacker page read the gateway's response cross-origin.

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-209)
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

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}
```

**File:** core/services/gateway/network/httpserver_test.go (L218-231)
```go
func TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards(t *testing.T) {
	t.Parallel()
	_, handler, url := startNewServer(t, 100_000, 100_000, true,
		[]string{"https://*.ethereum.org", "https://*.valid.domain.com", "http://example.gov:8080"})

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin := "https://ethereum.remix.org"                                                 // doesn't end with ethereum.org
	resp, respBytes := sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Methods"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Headers"))
```
