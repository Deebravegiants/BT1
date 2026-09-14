### Title
CORS wildcard-origin allowlist check in the Gateway HTTP server accepts attacker-controlled subdomain-confusable origins via unanchored suffix matching - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's internet-facing HTTP server (`core/services/gateway/network/httpserver.go`) validates the `Origin` header against a configured CORS allowlist that supports wildcard entries like `*.example.com`. The wildcard match is implemented with a raw `strings.HasSuffix` call with no dot-boundary check, so any origin that merely ends with the configured suffix (e.g. `evilexample.com` against an allowlisted `*.example.com`) is treated as an allowed subdomain. This is the same bug class as CVE-2021-21291 (oauth2-proxy whitelist domain matching).

### Finding Description
`isAllowedOrigin` parses both the incoming `Origin` header and each configured allowed origin, then for wildcard entries strips the `*.` prefix and does: [1](#0-0) 

There is no check that `originHost` has a `.` immediately preceding the stripped `allowedHost`, so `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true` even though `evilethereum.org` is not a subdomain of `ethereum.org`. Given a configuration such as `CORSAllowedOrigins = ["https://*.ethereum.org"]`, an attacker who controls (or registers) a domain like `https://evilethereum.org` or `https://notethereum.org` will pass this check.

When the check succeeds, `handleRequest` reflects the caller-supplied `Origin` value back in the `Access-Control-Allow-Origin` response header: [2](#0-1) 

The existing test suite only validates the intended "does not end with the domain" negative case (`https://ethereum.remix.org`) and positive subdomain cases, but does not test the subdomain-confusion case (`evilethereum.org`), so the unanchored suffix bug is not caught by the current tests: [3](#0-2) 

### Impact Explanation
This is the Gateway's public-facing HTTP entrypoint used to process external requests (`ProcessRequest`) for capability/handler traffic, gated by `CORSEnabled`/`CORSAllowedOrigins` config: [4](#0-3) 
An operator who configures a wildcard allowlist entry (e.g. `*.ethereum.org`, as shown in the existing tests) intends to scope browser-based cross-origin access to trusted subdomains only. Because of the missing dot-boundary check, an attacker who controls a similarly-suffixed domain can have their origin accepted, causing the Gateway to set `Access-Control-Allow-Origin` to the attacker's origin. This allows a malicious webpage to make cross-origin browser requests to the Gateway API and read the responses, which is a cross-origin response confusion / allowlist-bypass condition consistent with the reported bug class.

### Likelihood Explanation
Exploitation requires: (1) the operator has `CORSEnabled = true` with a wildcard allowlist entry, and (2) an attacker registers or controls a domain textually ending in the same suffix (a low-cost, purchasable condition, e.g. `notethereum.org` for `*.ethereum.org`). No privileged access or insider position is required — any unprivileged actor able to register a domain and lure a victim to a page can trigger this from the browser. The wildcard-CORS feature is present and exercised in tests, indicating it is an actively used configuration option, not a dead code path.

### Recommendation
Fix `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` to require a dot boundary (or exact equality) when matching the wildcard suffix, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
Add regression tests covering suffix-confusable domains (e.g. `evilethereum.org`, `notethereum.org` against `*.ethereum.org`) to prevent regressions.

### Proof of Concept
1. Configure the Gateway HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request to the Gateway's HTTP endpoint with header `Origin: https://evilethereum.org`.
3. Observe that `isAllowedOrigin` returns `true` (because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`), and the response includes `Access-Control-Allow-Origin: https://evilethereum.org`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`, as done in `handleRequest`: [5](#0-4) 
4. A browser page hosted at `https://evilethereum.org` can now make cross-origin fetch requests to the Gateway and read the responses, despite not being an intended subdomain of `ethereum.org`.

### Citations

**File:** core/services/gateway/network/httpserver.go (L33-55)
```go
type HTTPRequestHandler interface {
	ProcessRequest(ctx context.Context, rawMessage []byte, auth string) (rawResponse []byte, httpStatusCode int)
}

// HealthChecker gates whether the user HTTP server should receive traffic.
type HealthChecker func(context.Context) error

type HTTPServerConfig struct {
	Host                   string
	Port                   uint16
	TLSEnabled             bool
	TLSCertPath            string
	TLSKeyPath             string
	Path                   string
	ContentTypeHeader      string
	ReadTimeoutMillis      uint32
	WriteTimeoutMillis     uint32
	RequestTimeoutMillis   uint32
	MaxRequestBytes        int64
	MaxRequestBytesLimiter limits.BoundLimiter[config.Size] // supersedes MaxRequestBytes, if set
	CORSEnabled            bool
	CORSAllowedOrigins     []string
}
```

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
