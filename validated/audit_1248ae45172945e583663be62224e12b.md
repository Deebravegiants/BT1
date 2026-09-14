I have enough to write up the finding.

### Title
CORS `isAllowedOrigin` wildcard suffix match lacks a label boundary, allowing origin allowlist bypass — ([File: core/services/gateway/network/httpserver.go])

### Summary
The Gateway's internet-facing HTTP server implements CORS origin validation in `isAllowedOrigin`, which checks a browser-supplied `Origin` header against an operator-configured `CORSAllowedOrigins` list. For wildcard entries (`*.domain.com`), it strips the `*.` prefix and checks `strings.HasSuffix(originHost, allowedHost)` with no boundary/dot check before the suffix, exactly analogous to the unanchored-regex host-suffix bug in the reported CKAN advisory.

### Finding Description
`isAllowedOrigin` parses both the request's `Origin` header and each configured allowed origin via `splitURL`, then for wildcard entries does: [1](#0-0) 

The wildcard branch strips `*.` and performs `strings.HasSuffix(originHost, allowedHost)` without verifying that the character preceding the matched suffix is a `.` (i.e., a proper subdomain boundary). Because of this, any hostname that merely ends with the allowed domain string as a byte sequence — even when concatenated directly onto an unrelated label with no dot separator — passes the check. For example, if the operator configures `CORSAllowedOrigins: ["https://*.ethereum.org"]`, the stripped allowed host is `ethereum.org`, and an origin such as `https://evilethereum.org` satisfies `strings.HasSuffix("evilethereum.org", "ethereum.org") == true`, despite `evilethereum.org` being a completely different, attacker-registrable domain unrelated to `ethereum.org`. The same applies to any allowed second-level domain being spoofed by prefixing an arbitrary string directly before it without a dot (e.g., `notvalid.domain.com` bypass via `xvalid.domain.com` style typosquats, or `attacker-remix.ethereum.org`-style tricks where the attacker fully controls the label immediately preceding the real suffix).

This mirrors the CKAN `isValidMqaServer` root cause precisely: the check validates that a string *contains the trusted substring as a suffix*, but never enforces that the substring boundary aligns with a structural delimiter (`.` for DNS labels, in the CKAN case the host boundary after a hostname). The existing unit tests only cover the exact-match and true-subdomain cases and do not exercise the boundary-omission case, so the gap is unexercised in CI. [2](#0-1) 

### Impact Explanation
On a match, the server reflects the attacker-controlled `Origin` value back verbatim in `Access-Control-Allow-Origin`, along with `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`: [3](#0-2) 

Since this check gates cross-origin browser access to the Gateway's `ProcessRequest` handler (an unprivileged, internet-facing endpoint accepting arbitrary client messages), an attacker who registers/controls a domain crafted to satisfy the flawed suffix check (e.g., `evil<allowed-domain>`) can host a web page that issues cross-origin requests to the Gateway from a victim's browser and read the JSON-RPC-style responses that would otherwise be restricted to the operator's intended trusted frontends. This is a CORS allowlist bypass rooted in the same CWE-20/CWE-625 class (improper input validation via unanchored substring matching) as the CKAN advisory.

### Likelihood Explanation
Exploitability depends on the operator having configured at least one wildcard `CORSAllowedOrigins` entry (e.g., `*.chain.link`), which is a documented/supported configuration pattern (see the test coverage and sample configs referencing `CORSAllowedOrigins`). Any attacker able to register or control a domain string ending in the same byte sequence as an allowed domain (which is trivial — domain registration is unrestricted, e.g., `evilchain.link` vs `*.chain.link`) can exploit this without any privileges, from a plain browser tab, against the internet-facing Gateway.

### Recommendation
Enforce a proper label boundary when doing suffix comparisons for wildcard CORS origins — require that the character immediately preceding the matched suffix be `.`, equivalently check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix`.

### Proof of Concept
Given `CORSAllowedOrigins: []string{"https://*.ethereum.org"}`, sending a request with header `Origin: https://evilethereum.org` to the Gateway's HTTP endpoint will cause `isAllowedOrigin` to return `true` (since `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`), and the server will reflect `Access-Control-Allow-Origin: https://evilethereum.org` in the response, per the logic at: [1](#0-0)

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
