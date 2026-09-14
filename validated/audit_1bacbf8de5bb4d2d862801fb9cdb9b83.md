Confirmed: the wildcard-origin check in `isAllowedOrigin` is vulnerable to a suffix-matching bypass. This is a genuine, unprivileged-actor-reachable analog to the CVE's "spoofed origin passes an SOP-style check" bug class, on the internet-facing Gateway user HTTP server.

### Title
CORS wildcard allowlist bypass via naive suffix match allows malicious origin impersonation - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Chainlink Gateway's user-facing HTTP server implements a custom CORS origin allowlist check in `isAllowedOrigin`. When an allowed origin entry uses a wildcard subdomain form (e.g. `https://*.ethereum.org`), the code strips the `*.` prefix and then checks whether the request's `Origin` header host merely ends with that suffix, using `strings.HasSuffix(originHost, allowedHost)`. Because there is no check that a domain separator (`.`) precedes the suffix, any attacker-registered domain that happens to end with the same characters (e.g. `evilethereum.org`) is incorrectly treated as a valid subdomain of the allowed origin (`ethereum.org`).

### Finding Description
`isAllowedOrigin` parses both the incoming request's `Origin` header and each configured `CORSAllowedOrigins` entry with `splitURL`, then compares scheme, port, and host. For wildcard entries the comparison is: [1](#0-0) 
This strips `*.` from `*.ethereum.org` to get `ethereum.org`, then does a raw suffix check against the origin's host. A host like `evilethereum.org` (no subdomain separator) satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org")`, so an attacker who registers any domain ending in the allowed suffix is granted the same trust as a legitimate subdomain of the operator's chosen origin, even though it is a completely different, attacker-controlled origin — analogous to the CVE's SOP bypass via a spoofed, non-matching origin value.

The result of a successful match is then reflected directly back to the browser: [2](#0-1) 
This sets `Access-Control-Allow-Origin` to the attacker's exact spoofed origin value (not a static string), which browsers accept because it matches the `Origin` request header, allowing the attacker's origin to make credentialed/authenticated cross-origin requests (with `Access-Control-Allow-Headers: Content-Type` allowing JSON bodies) to the Gateway's `/user` endpoint that a legitimate `*.ethereum.org` origin (e.g. Remix IDE) would be entitled to.

### Impact Explanation
An attacker who registers a domain such as `evilethereum.org`, `fakeethereum.org`, or any string ending in an operator's configured wildcard suffix (e.g. `notyourvalid.domain.com` for `*.valid.domain.com`) can host a malicious web page that issues cross-origin JSON-RPC requests to the Gateway's user-facing HTTP server and receive responses with the origin reflected in `Access-Control-Allow-Origin`. This effectively bypasses the operator's intended origin allowlist for the internet-facing Gateway, enabling request forgery/impersonation from an unauthorized origin against a component whose purpose is to broker requests between web/off-chain users and DON node handlers.

### Likelihood Explanation
Exploitation only requires registering an inexpensive domain whose name ends with the victim's configured wildcard suffix (a widely documented CORS suffix-matching pitfall) and does not require any privileged access, credentials, or node compromise — it is reachable by any unprivileged external client hitting the Gateway's `UserServerConfig` HTTP endpoint whenever `CORSEnabled = true` and a wildcard entry is configured, as shown in the integration test config using `CORSAllowedOrigins = ["https://remix.ethereum.org"]`-style wildcard entries: [3](#0-2) 
and exercised directly by the existing wildcard tests: [4](#0-3) 

### Recommendation
Fix the suffix check to require a proper subdomain boundary, e.g. verify `originHost == allowedHost` or `strings.HasSuffix(originHost, "."+allowedHost)` after stripping `*.`, rather than a bare `strings.HasSuffix` match. Alternatively, split the origin host on `.` and compare the trailing labels exactly, or use a well-tested URL/domain-matching library instead of hand-rolled suffix comparison.

### Proof of Concept
1. Configure the Gateway `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From an attacker-controlled site hosted at `https://evilethereum.org`, send a `POST` request to the Gateway's `/user` path with header `Origin: https://evilethereum.org`.
3. Observe in `isAllowedOrigin`: `allowedHost` becomes `ethereum.org` after stripping `*.`; `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`, so the function returns `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilethereum.org` (and permissive methods/headers), allowing the attacker's page to make cross-origin requests to the Gateway that should only be permitted from genuine `*.ethereum.org` subdomains, per the logic in [5](#0-4) .

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

**File:** core/services/gateway/network/httpserver.go (L195-203)
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

**File:** core/services/gateway/integration_tests/gateway_integration_test.go (L59-60)
```go
CORSEnabled = true
CORSAllowedOrigins = ["https://remix.ethereum.org"]
```

**File:** core/services/gateway/network/httpserver_test.go (L152-166)
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

```
