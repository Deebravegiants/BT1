## Analysis

I found a concrete CORS allowlist-bypass bug in the Chainlink Gateway's HTTP server that matches the CWE-346 (Origin Validation Error) bug class from the referenced advisory.

### Root cause

The wildcard-origin matcher in `isAllowedOrigin` does a naive suffix check without verifying a label (dot) boundary between the wildcard prefix and the matched suffix: [1](#0-0) 

Given `allowedHost = "*.ethereum.org"`, the code strips `"*."` leaving `"ethereum.org"`, then checks `strings.HasSuffix(originHost, "ethereum.org")`. A sibling domain like `evilethereum.org` (registerable by any attacker, no dot separator) also satisfies `HasSuffix`, so it is wrongly treated as a subdomain of `ethereum.org` and granted CORS allow-listing.

This is invoked from the request handler, which sets `Access-Control-Allow-Origin` to the (attacker-controlled) `Origin` value whenever `isAllowedOrigin` returns true: [2](#0-1) 

The existing tests only cover non-matching suffixes like `ethereum.remix.org` (which correctly fails) but never test a sibling-domain case such as `evilethereum.org`, so this bypass is untested: [3](#0-2) 

The `UserServerConfig` (browser/user-facing gateway endpoint, e.g. port 8080/`/user`) is the component that enables `CORSEnabled`/`CORSAllowedOrigins`, making this reachable from an unprivileged web client: [4](#0-3) 

### Title
CORS Wildcard-Origin Allowlist Bypass via Missing Dot-Boundary Check - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's `httpServer.isAllowedOrigin` function implements wildcard origin matching (`*.example.com`) using `strings.HasSuffix` on the origin host and the wildcard's suffix, without requiring a `.` boundary before the matched suffix. This lets any attacker who registers a domain that merely ends with the same characters (e.g. `evilethereum.org` for an allowlist entry `*.ethereum.org`) pass origin validation and receive `Access-Control-Allow-Origin` for that spoofed origin.

### Finding Description
`isAllowedOrigin` splits the configured allowed origins and requested `Origin` header into scheme/host/port and, for wildcard entries, strips the `"*."` prefix and checks `strings.HasSuffix(originHost, allowedHost)`. Because this is a raw string suffix comparison rather than a label-aware subdomain check, a domain like `evilethereum.org` incorrectly satisfies `HasSuffix("evilethereum.org", "ethereum.org")`, even though it is not a subdomain of `ethereum.org` at all — it's an entirely separate, attacker-registrable domain name. [5](#0-4) 
This is the same bug class as the reported advisory (CWE-346, Origin Validation Error): insufficiently strict Origin validation lets an untrusted origin be treated as trusted.

### Impact Explanation
When `CORSEnabled = true` and an operator configures a wildcard allowlist entry (a documented, supported pattern per `sample_config.toml`/`sample_config_tls.toml`), any attacker can register a low-cost sibling domain and have their malicious webpage's cross-origin requests to the Gateway's `UserServerConfig` HTTP endpoint pass CORS validation. The server will then reflect the attacker's `Origin` in `Access-Control-Allow-Origin`, letting the attacker's page read cross-origin JSON-RPC responses from the Gateway on behalf of a victim's browser — this is an allowlist/CORS bypass enabling cross-user response confusion/leakage for any legitimate session or credential a victim's browser attaches to the request.

### Likelihood Explanation
Exploitability only requires: (1) the operator uses a wildcard entry in `CORSAllowedOrigins` (a supported, documented configuration pattern), and (2) an attacker registers a cheap domain sharing the suffix characters. No network position or DNS rebinding is even required — this is a pure string-matching bug reachable directly over the internet-facing Gateway user server. This is a straightforward, high-likelihood bug for any deployment using wildcard CORS entries.

### Recommendation
Fix the wildcard suffix check to require a proper label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".ethereum.org" (keep the leading dot)
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
Add test cases for sibling domains (e.g. `evilethereum.org` vs `*.ethereum.org`) to `httpserver_test.go` to prevent regression.

### Proof of Concept
1. Configure Gateway `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request with header `Origin: https://evilethereum.org`.
3. `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`.
4. The response includes `Access-Control-Allow-Origin: https://evilethereum.org`, allowing a page hosted on the attacker-registered `evilethereum.org` domain to make cross-origin requests to the Gateway and read the JSON-RPC responses, despite not being a genuine subdomain of the intended `ethereum.org` allowlist entry.

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

**File:** core/services/gateway/network/httpserver_test.go (L218-232)
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
