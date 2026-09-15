### Title
CORS `Origin` allowlist bypass via improper wildcard suffix matching in gateway HTTP server - (File: core/services/gateway/network/httpserver.go)

### Summary
The gateway's user-facing HTTP server derives whether to reflect a client-supplied `Origin` header (and grant CORS credentials/headers) using `isAllowedOrigin`, which for wildcard entries (`*.domain.com`) reduces the check to a raw string suffix match without verifying a domain-label boundary. [1](#0-0) 

### Finding Description
`isAllowedOrigin` parses both the incoming `Origin` header and each configured allowed origin via `splitURL`, then compares scheme, port, and host. [2](#0-1)  For entries prefixed with `*.`, the code strips the `*.` and does `strings.HasSuffix(originHost, allowedHost)`: [3](#0-2) 

This is a raw string-suffix check, not a domain-label boundary check. If an operator configures `CORSAllowedOrigins = ["https://*.ethereum.org"]` intending to allow only subdomains of `ethereum.org`, the reduced allowed-host string is `ethereum.org`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`. An attacker who registers a domain like `evilethereum.org` (or any domain textually ending in `ethereum.org` without a preceding dot, e.g. `notethereum.org`) can send that as the `Origin` header and have it accepted as a legitimate subdomain, since there is no check that the character preceding the matched suffix is a `.` or that `originHost` boundary aligns with a full label.

This directly parallels the CVE-2020-8124 bug class (improper validation/sanitization of URL components allowing a security check to be bypassed): the URL/host is parsed and then a hostname-allowlist decision is made from string operations that don't enforce correct component boundaries, letting an attacker-controlled string satisfy the check while representing a different origin than intended.

### Impact Explanation
If exploited, this causes `handleRequest` to reflect the attacker's malicious origin into `Access-Control-Allow-Origin` and set permissive CORS headers: [4](#0-3)  This allows a browser-based unprivileged attacker hosting content on a domain that merely *ends with* the configured suffix (not an actual subdomain) to make cross-origin requests to the gateway's user-facing endpoint that appear to come from an authorized origin, undermining the operator's intended origin allowlist for the internet-facing gateway. This is a concrete allowlist-bypass matching the "Validate" criteria.

### Likelihood Explanation
Exploitability depends entirely on the operator's CORS configuration: only if `CORSEnabled = true` and `CORSAllowedOrigins` contains a wildcard entry (`*.domain.tld`) is this reachable, and the attacker additionally needs to control/register a domain that textually ends with the configured suffix. The sample config ships with `CORSEnabled = false` by default. [5](#0-4)  Existing tests demonstrate the wildcard-matching behavior is intentional/expected as currently coded (matching `remix.ethereum.org` against `*.ethereum.org`), but none of the tests exercise the boundary-confusion case (e.g., `evil-ethereum.org` or `notethereum.org` matching `*.ethereum.org`), so the gap is untested. [6](#0-5) 

### Recommendation
Enforce a proper label boundary when doing wildcard suffix matching: after stripping `*.`, require that `originHost` either equals `allowedHost` or ends with `"." + allowedHost` (i.e., check `strings.HasSuffix(originHost, "."+allowedHost)` in addition to/instead of the raw `HasSuffix`). This ensures `evilethereum.org` does not match `*.ethereum.org` while `sub.ethereum.org` still does. Add regression tests for adjacent-string domains (e.g. `notethereum.org`, `evilethereum.org.attacker.com`) to lock in the fix.

### Proof of Concept
1. Configure the gateway with:
   ```
   CORSEnabled = true
   CORSAllowedOrigins = ["https://*.ethereum.org"]
   ```
2. Send a request to the user-facing gateway endpoint with header:
   ```
   Origin: https://evilethereum.org
   ```
3. `splitURL` parses `originHost = "evilethereum.org"`, and the configured `allowedHost` after stripping `*.` is `"ethereum.org"`. [3](#0-2) 
4. `strings.HasSuffix("evilethereum.org", "ethereum.org")` evaluates to `true`, so `isAllowedOrigin` returns `true`.
5. The response includes `Access-Control-Allow-Origin: https://evilethereum.org`, permitting a page hosted on the attacker's unrelated domain to make credentialed/cross-origin requests to the gateway that the operator intended to restrict to genuine `*.ethereum.org` subdomains.

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
