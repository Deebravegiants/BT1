## Title
CORS wildcard origin matching allows domain-suffix spoofing without dot-boundary check - (`core/services/gateway/network/httpserver.go`)

### Summary
The Chainlink gateway's HTTP server implements a wildcard CORS allowlist (e.g. `*.ethereum.org`) intended to permit only subdomains of a trusted domain. The wildcard-matching logic strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` with no verification that a `.` (subdomain boundary) precedes the matched suffix. Any attacker who registers a domain whose name literally ends with the configured suffix string (not an actual subdomain) is treated as an allowed origin, letting an unprivileged, internet-based actor bypass the CORS allowlist on the gateway's public HTTP endpoint.

### Finding Description
`isAllowedOrigin` performs origin comparisons per configured `CORSAllowedOrigins` entry: [1](#0-0) 

The wildcard branch is:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

`strings.HasSuffix` matches any string that ends with `allowedHost`, without requiring a `.` immediately before it. For a configured allowlist entry `*.ethereum.org`, `allowedHost` becomes `ethereum.org`. This matches legitimate subdomains like `remix.ethereum.org`, but it equally matches any attacker-registered domain that simply ends with the literal string `ethereum.org` with no separating dot — e.g. `evil-ethereum.org` or `notethereum.org` (an attacker-owned domain, not a subdomain of `ethereum.org`). This is the same bug class as CVE-2023-1668: a wildcard-style match that is applied too broadly because a required boundary/qualifier is not checked, causing the rule to be satisfied by unintended inputs.

The result is then used to reflect the caller-supplied `Origin` header directly into `Access-Control-Allow-Origin`: [3](#0-2) 

so any browser page hosted on the spoofed domain is granted cross-origin access to the gateway's JSON-RPC endpoint as though it were a trusted allowlisted origin.

### Impact Explanation
This is an allowlist bypass reachable by any unprivileged internet actor who simply registers a domain string ending with the configured suffix — no compromise of the real trusted domain is required. Any browser-based client visiting the attacker's page can then interact cross-origin with the gateway's internet-facing HTTP endpoint as an "allowed" origin, undermining the operator's intended CORS trust boundary for that gateway deployment (e.g., trusted dApp frontends such as `*.ethereum.org` or `*.valid.domain.com` configured in production, see `core/scripts/gateway/sample_config.toml`). The severity depends on what the gateway response contains and whether browser-stored credentials/tokens end up exposed to scripts on the spoofed origin.

### Likelihood Explanation
Likelihood is high for any deployment that uses a wildcard entry in `CORSAllowedOrigins` (a documented and tested configuration option, see `TestHTTPServer_HandleRequest_CORSEnabled_FromAllowedOriginWildcards`), since exploitation only requires registering an appropriately-named domain — an inexpensive and fully attacker-controlled action requiring no network position or privileged credentials.

### Recommendation
Change the wildcard suffix check to require a subdomain boundary, e.g.:
```go
if strings.HasSuffix(originHost, "."+allowedHost) || originHost == allowedHost {
    return true
}
```
so `evil-ethereum.org` no longer satisfies `*.ethereum.org`, while `remix.ethereum.org` still does.

### Proof of Concept
Given gateway config `CORSAllowedOrigins: ["https://*.ethereum.org"]`:
1. Attacker registers `https://notethereum.org` (or any domain literally ending in `ethereum.org`).
2. Attacker hosts a page there and has a victim's browser send a cross-origin request to the gateway's HTTP endpoint with `Origin: https://notethereum.org`.
3. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and returns `true` because `strings.HasSuffix("notethereum.org", "ethereum.org")` is `true`, even though `notethereum.org` is not a subdomain of `ethereum.org`.
4. The gateway responds with `Access-Control-Allow-Origin: https://notethereum.org`, letting the attacker's page make authorized cross-origin requests/read responses, matching the existing wildcard test pattern at [4](#0-3) .

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
