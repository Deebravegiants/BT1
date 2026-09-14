The chainlink gateway's user-facing HTTP server implements its own CORS validation in [1](#0-0)  rather than a per-route library configuration, so the exact hapi bug class (CORS enabled at connection level but disabled per-route, causing preflight/actual-request header inconsistency) has no direct structural analog here — the gateway's `UserServerConfig.CORSEnabled` flag is applied uniformly to every request hitting `handleRequest`, as shown at [2](#0-1) .

However, tracing the actual origin-validation logic surfaced a real, related "incorrect CORS origin handling" defect that fits the same CWE-284 bug class (improper access control allowing cross-origin activity that should be forbidden):

### Title
Wildcard CORS origin suffix-matching bypass allows unauthorized cross-origin access to Gateway user API - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's user-facing HTTP server (`UserServerConfig`) validates CORS origins with a wildcard-matching routine that uses a plain `strings.HasSuffix` check without verifying a preceding domain-label separator (`.`). This allows any attacker-registered domain that merely ends with the same character sequence as an allowed wildcard domain (not an actual subdomain of it) to be treated as an allowed CORS origin.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard entry (e.g. `*.ethereum.org` → `ethereum.org`) and then checks `strings.HasSuffix(originHost, allowedHost)`: [3](#0-2) 

This is a substring/suffix check, not a domain-label check. A host such as `evil-ethereum.org` or `notethereum.org` literally ends with the string `ethereum.org` and will pass `strings.HasSuffix(originHost, "ethereum.org")`, even though it is an entirely different, attacker-registrable domain unrelated to `ethereum.org`. Proper subdomain validation requires either an exact match or a match preceded by a `.` (i.e., `strings.HasSuffix(originHost, "."+allowedHost)`), which this code omits.

Because `handleRequest` reflects the received `Origin` header back as `Access-Control-Allow-Origin` whenever `isAllowedOrigin` returns true, this bug lets an attacker who controls a domain with the right suffix (no dot required) obtain valid CORS headers for the Gateway user server: [4](#0-3) 

The wildcard configuration mechanism is exercised in gateway configs such as `sample_config.toml`/`sample_config_tls.toml` and integration tests, confirming wildcard origins are a supported, real-world configuration option for the user-facing gateway server: [5](#0-4) 

### Impact Explanation
If an operator configures `CORSAllowedOrigins` with a wildcard entry (e.g., `https://*.example.com`) intending to allow only subdomains of `example.com`, an unprivileged external attacker who registers a lookalike domain ending in the same suffix (e.g., `https://evil-example.com`) can have that origin reflected in `Access-Control-Allow-Origin`. A browser page hosted on the attacker's domain can then make authenticated/credentialed cross-origin requests to the Gateway's user API that browsers would otherwise block, defeating the operator's intended origin restriction — directly matching the hapi advisory's "allow cross-origin activities that are expected to be forbidden" impact.

### Likelihood Explanation
Exploitability depends on: (1) the Gateway operator enabling CORS and configuring at least one wildcard origin (`*.domain.tld`), and (2) an attacker being able to register or control a domain ending in that same string without a separating dot. Both conditions are plausible in real deployments since wildcard origins are a documented, supported configuration pattern, and domain registration for a suffix-matching string is trivial and requires no special privilege.

### Recommendation
Fix the wildcard suffix check to require a domain-label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This ensures only actual subdomains (or the exact domain) match, not arbitrary strings sharing a suffix.

### Proof of Concept
1. Configure the Gateway's `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser page hosted at `https://evil-ethereum.org` (registrable by any attacker, unrelated to the legitimate `ethereum.org`), send a request to the Gateway user endpoint with header `Origin: https://evil-ethereum.org`.
3. Observe the server responds with `Access-Control-Allow-Origin: https://evil-ethereum.org`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, and `Access-Control-Allow-Headers: Content-Type`, incorrectly treating `evil-ethereum.org` as an allowed subdomain of `ethereum.org`.
4. The attacker's page can now make cross-origin requests to the Gateway user API that the browser would otherwise disallow.

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
