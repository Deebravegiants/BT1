## Finding: CORS wildcard-origin allowlist in the Gateway HTTP server uses an unanchored suffix check

The reported CefSharp bug class is a **path/string "boundary" check implemented as a raw prefix/suffix comparison instead of enforcing a proper separator boundary**, letting an attacker-controlled sibling value (`www2`) be accepted because it merely *starts with* the allowed root string (`www`). The same bug class exists in this repo's Gateway CORS origin validator, but on the *suffix* side of a wildcard host check.

### Title
CORS wildcard-origin allowlist bypass via missing dot-boundary check in `isAllowedOrigin` - (File: `core/services/gateway/network/httpserver.go`)

### Summary
`httpServer.isAllowedOrigin` validates the `Origin` header against `CORSAllowedOrigins` entries. For wildcard entries like `*.ethereum.org`, it strips the `*.` prefix and then checks `strings.HasSuffix(originHost, allowedHost)` with no boundary/dot check, so any origin host that merely ends with the allowed suffix — including one with no subdomain separator, e.g. `evilethereum.org` — passes the check for an allowed pattern `*.ethereum.org`.

### Finding Description [1](#0-0) 

The relevant block:
```go
// check for wildcard host match (e.g., *.remix.com)
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
```
`allowedHost` becomes `"ethereum.org"` after stripping `*.`. `strings.HasSuffix(originHost, "ethereum.org")` is then true for `originHost` values such as `"evilethereum.org"`, `"notethereum.org"`, or `"fakeethereum.org"` — none of which are actual subdomains of `ethereum.org`, but which all satisfy the raw suffix comparison because there is no enforced `.` boundary between the attacker-chosen label and the allowed suffix. This is structurally identical to the CefSharp `FolderSchemeHandlerFactory` issue: a string containment/boundary check (`StartsWith`/`HasSuffix`) is used in place of a proper hierarchical boundary check (path-separator vs. domain-label-separator), so a sibling/adjacent value that is not actually inside the intended scope is incorrectly accepted.

This check gates `isAllowedOrigin`, which is called directly from the Gateway's internet-facing HTTP request handler: [2](#0-1) 

```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			...
```
`handleRequest` is the handler registered for the Gateway's public User HTTP server path (see `NewHTTPServer`/`HTTPRequestHandler`), which is unauthenticated/browser-reachable — exactly the "internet-facing gateway" surface called out as in-scope.

### Impact Explanation
If an operator configures `CORSAllowedOrigins` with a wildcard entry (e.g. `*.mycompany.com`), an attacker who registers or controls a domain that merely ends with that suffix without a dot boundary (e.g. `evilmycompany.com`) can have their web page's cross-origin requests to the Gateway's user-facing HTTP endpoint be granted `Access-Control-Allow-Origin` matching their own origin. A victim's browser visiting the attacker's page would then allow the attacker's script to read the Gateway's JSON-RPC responses for requests made with the victim's ambient credentials/cookies (cross-user response confusion / CORS allowlist bypass), rather than being restricted to genuine subdomains of the trusted domain.

### Likelihood Explanation
Exploitability depends entirely on the deployed `CORSAllowedOrigins` configuration containing a wildcard entry (`*.example.com`) and on the existence/registerability of a sibling domain sharing that suffix without a dot separator (e.g. buying `notexample.com`). This is a realistic, low-cost attack for any operator who uses wildcard CORS entries, since domain suffix collisions are trivial for an attacker to engineer (register any domain ending in the target suffix).

### Recommendation
Change the wildcard match to require a dot boundary (or exact match), e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
This mirrors the correct fix pattern for the referenced advisory: replace a raw prefix/suffix string check with one that enforces the structural separator (path separator for filesystem paths, `.` for DNS labels).

### Proof of Concept
1. Configure the Gateway with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. From a browser page hosted at `https://evilethereum.org` (no relation to `ethereum.org`), send a cross-origin request to the Gateway's user HTTP endpoint with `Origin: https://evilethereum.org`.
3. Observe the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, i.e., `isAllowedOrigin` returns `true` even though `evilethereum.org` is not a subdomain of `ethereum.org` — confirmed by the code path at [3](#0-2) , and contrasted with the existing test suite which only exercises well-formed subdomains such as `remix.ethereum.org`: [4](#0-3) .

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
