## Title
CORS Origin Allowlist Bypass via Unanchored Suffix Matching in Gateway HTTP Server - (File: `core/services/gateway/network/httpserver.go`)

### Summary
The gateway's `httpServer.isAllowedOrigin` function validates browser `Origin` headers against a configured wildcard allowlist (e.g. `*.ethereum.org`) using a raw string-suffix comparison (`strings.HasSuffix`) instead of a dot-anchored subdomain check. This mirrors the CVE's root cause class: a hostname/domain "matcher" that fails to enforce a proper label boundary, letting an attacker-controlled hostname that merely *ends with* the trusted suffix be treated as a legitimate subdomain — a wildcard-depth allowlist bypass.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard allowed-origin and then checks the incoming `Origin` host with `strings.HasSuffix`: [1](#0-0) 

There is no check that the character immediately preceding the matched suffix is a `.` (dot) label separator. As a result, any registrable domain that happens to end with the exact allowed-suffix string — not just true subdomains — is treated as trusted. For example, if the gateway is configured with `CORSAllowedOrigins = ["https://*.ethereum.org"]`, the allowed host becomes `ethereum.org`, and `strings.HasSuffix("myethereum.org", "ethereum.org")` returns `true`, even though `myethereum.org` is a completely independent, attacker-registrable second-level domain, not a subdomain of `ethereum.org`.

The existing test suite only exercises cases where the extra prefix is separated by another dot-delimited label (e.g. `ethereum.remix.org` correctly failing to match `*.ethereum.org`) or differs in scheme/port, but never tests the no-dot-boundary concatenation case: [2](#0-1) 

This function directly gates whether the internet-facing gateway HTTP server reflects the caller's `Origin` back in `Access-Control-Allow-Origin` and enables cross-origin browser access to the endpoint: [3](#0-2) 

This is the same bug class as ALPINE-CVE-2026-48618: a hostname authorization check performing an insufficiently anchored comparison, letting a crafted/registered hostname bypass an intended wildcard-domain trust boundary.

### Impact Explanation
An attacker who registers a domain that textually ends with an allowed wildcard suffix (e.g. `myethereum.org` when `*.ethereum.org` is trusted) can host a page at that origin and have the gateway believe it is a trusted first-party subdomain, causing the server to set `Access-Control-Allow-Origin` to that attacker-controlled origin. This is a concrete allowlist bypass of the CORS origin boundary intended to restrict which web frontends may interact cross-origin with the gateway's job/request-handling API, weakening the isolation the allowlist was meant to enforce.

### Likelihood Explanation
Exploitability requires only that an operator configure a wildcard `CORSAllowedOrigins` entry (a supported and documented configuration pattern) and that an attacker register or control a domain ending in that suffix — both realistic conditions since second-level domain names ending in a trusted suffix string are commonly available for registration.

### Recommendation
Change the wildcard match to require a dot boundary before the suffix, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
so `originHost` must equal the base domain or end with `.` + base domain, not just share a raw string suffix.

### Proof of Concept
1. Configure the gateway with `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request to the gateway's HTTP path with header `Origin: https://myethereum.org`.
3. `isAllowedOrigin` strips `*.` to get `allowedHost = "ethereum.org"`, then evaluates `strings.HasSuffix("myethereum.org", "ethereum.org")`, which is `true`.
4. The server responds with `Access-Control-Allow-Origin: https://myethereum.org`, treating the unrelated domain `myethereum.org` as a trusted subdomain of `ethereum.org`, per [1](#0-0) .

### Citations

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
