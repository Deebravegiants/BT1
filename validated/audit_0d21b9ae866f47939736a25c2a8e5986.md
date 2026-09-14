## Analysis: CORS Wildcard Origin Bypass in Chainlink Gateway (analog to CVE-2021-42135 glob-policy privilege issue)

The Vault CVE stems from a glob/wildcard matcher granting access beyond the intended scope because the matching logic didn't respect the semantic boundary of the pattern. The closest concrete analog in this codebase is the internet-facing Gateway HTTP server's wildcard CORS-origin allowlist check, which has the same class of flaw: a suffix match with no boundary character check, so an attacker-registered domain (not a real subdomain) is treated as if it matched the intended wildcard pattern. [1](#0-0) 

### Title
CORS wildcard allowlist bypass via missing domain-boundary check in Gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's HTTP server implements custom CORS origin validation in `isAllowedOrigin`. For entries prefixed with `*.` it strips the `*.` prefix and then performs a raw string-suffix check (`strings.HasSuffix(originHost, allowedHost)`) with no verification that the matched suffix is preceded by a `.` boundary in the origin host. [2](#0-1) 

### Finding Description
Given an operator-configured allowlist entry such as `https://*.ethereum.org`, the intent is to allow only genuine subdomains of `ethereum.org` (e.g. `remix.ethereum.org`). The implementation strips the `*.` leaving `allowedHost = "ethereum.org"` and then checks `strings.HasSuffix(originHost, "ethereum.org")`. This check is satisfied by any origin host whose string literally ends with that suffix, regardless of whether a `.` boundary exists — e.g. `fakeethereum.org` (an attacker-registrable domain unrelated to `ethereum.org`) also satisfies `HasSuffix(originHost, "ethereum.org")`.

This exactly mirrors the Vault bug class: a glob/wildcard-style access-control pattern is matched using naive string comparison instead of respecting the structural boundary implied by the wildcard, so an unprivileged/untrusted actor (any domain owner) obtains a match that the operator did not intend to grant.

`handleRequest` uses the result of `isAllowedOrigin` directly to decide whether to reflect the `Origin` and grant `Access-Control-Allow-Origin`/`-Methods`/`-Headers`, enabling cross-origin `fetch`/`XHR` access to the gateway's `ProcessRequest` responses from the spoofed origin. [3](#0-2) 

### Impact Explanation
Any site an attacker controls whose hostname happens to end with the configured wildcard suffix (a trivially registrable domain, e.g. `evil-fakeethereum.org` for an allowlist entry `*.ethereum.org`) is granted the same CORS trust as legitimate subdomains. This allows an unprivileged, arbitrary web origin to issue cross-origin browser requests against the Gateway's HTTP endpoint and have the browser treat the response as CORS-approved, undermining the operator's intended origin restriction (an allowlist/CORS scoping bypass on the internet-facing gateway).

### Likelihood Explanation
Exploitability only requires registering/controlling a domain string that happens to share the suffix of a configured wildcard entry — no privileged access, no MITM, and no interaction with the node operator is required. The existing test suite only verifies the "happy path" wildcard matches (`*.ethereum.org` → `remix.ethereum.org`) and does not test suffix-collision domains, so the boundary gap is unguarded in practice. [4](#0-3) 

### Recommendation
When stripping the `*.` prefix, require that the matched suffix in `originHost` be preceded by a literal `.` (i.e., check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`) so that only true subdomains match, closing the boundary gap.

### Proof of Concept
1. Operator configures Gateway CORS allowlist: `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers/controls `https://fakeethereum.org` (note: not a subdomain — no leading dot before `ethereum.org`).
3. Attacker's page issues a cross-origin request to the Gateway endpoint with `Origin: https://fakeethereum.org`.
4. In `isAllowedOrigin`, `allowedHost` becomes `"ethereum.org"` after stripping `*.`; `strings.HasSuffix("fakeethereum.org", "ethereum.org")` returns `true`, so the function returns `true`.
5. `handleRequest` reflects `Access-Control-Allow-Origin: https://fakeethereum.org`, granting the attacker's origin the same cross-origin access as a legitimate `*.ethereum.org` subdomain would have received. [5](#0-4)

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

**File:** core/services/gateway/network/httpserver_test.go (L152-165)
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
