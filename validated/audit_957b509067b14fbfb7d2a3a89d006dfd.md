### Title
CORS Origin Allowlist Bypass via Missing Domain-Boundary Check in Wildcard Suffix Matching - (File: core/services/gateway/network/httpserver.go)

### Summary
The Gateway's internet-facing HTTP server validates the `Origin` header against a configured wildcard allowlist using a raw `strings.HasSuffix` comparison with no domain-separator boundary check. An attacker can register or control a domain that merely *ends with* the configured suffix (e.g. `evilethereum.org` for an allowlist entry `*.ethereum.org`) and be treated as a trusted subdomain, causing the Gateway to reflect the attacker's `Origin` in `Access-Control-Allow-Origin` and permit cross-origin access. [1](#0-0) 

### Finding Description
`isAllowedOrigin` splits the request `Origin` and each configured `CORSAllowedOrigins` entry into scheme/host/port, then for wildcard entries (`*.domain.com`) strips the `*.` prefix and checks `strings.HasSuffix(originHost, allowedHost)`. [2](#0-1) 

This is analogous to the reported bug class: a security decision (subdomain/hostname trust) is made on an externally supplied hostname string without validating that a `.` boundary actually exists between the wildcard label and the trusted suffix — just as the c-ares CVE stems from insufficient validation of DNS-returned hostname strings leading to acceptance of an attacker-controlled name as legitimate. Here, `HasSuffix` alone cannot distinguish `evil-ethereum.org` or `notarealethereum.org` from a genuine subdomain like `api.ethereum.org`, because both end in the literal bytes `ethereum.org`.

Concretely, for an operator configuration `CORSAllowedOrigins = ["https://*.ethereum.org"]`, the check reduces to `strings.HasSuffix(originHost, "ethereum.org")`. Any attacker-registered domain whose name simply ends in that string (no dot required before it), such as `https://evilethereum.org` or `https://fakeethereum.org`, satisfies the suffix test and is granted trusted-origin status. The existing test suite only exercises cases that don't share the suffix at all (e.g. `ethereum.remix.org`) or differ in scheme/port, so this boundary-omission case is untested. [3](#0-2) 

Once accepted, `handleRequest` reflects the attacker's `Origin` value verbatim into `Access-Control-Allow-Origin` and sets permissive `Access-Control-Allow-Methods`/`Access-Control-Allow-Headers`, enabling a page hosted on the attacker's spoofed-suffix domain to make cross-origin browser requests against the Gateway's user-facing HTTP endpoint and read the JSON-RPC responses. [4](#0-3) 

Any unprivileged actor who registers a domain with the vulnerable suffix (no special access required — this is purely a hostname-string comparison flaw, not a network/DNS/malicious-node issue) can exploit this from the internet-facing Gateway.

### Impact Explanation
This is an allowlist-bypass vulnerability in the internet-facing Gateway HTTP server. An attacker-controlled origin can be misclassified as trusted, letting a browser-based attacker page issue cross-origin requests to the Gateway endpoint and read the response (including any bearer-token-authenticated JSON-RPC payloads that a victim's browser might send/receive through the attacker page), which can lead to cross-user response confusion or leakage of workflow/DON response data intended only for the legitimate subdomain owner.

### Likelihood Explanation
Exploitability only requires the operator to configure a wildcard `CORSAllowedOrigins` entry (a supported, documented feature) and an attacker registering any domain name that happens to end with the same character sequence as the allowed suffix (e.g., `evilethereum.org` vs `*.ethereum.org`). No privileged access, malicious node/peer behavior, or network-layer manipulation is needed — it's a pure string-comparison logic flaw reachable from any browser client sending a crafted `Origin` header.

### Recommendation
Fix `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` to require a `.` boundary (or exact segment match) before the trusted suffix, e.g. check `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)` instead of a bare `strings.HasSuffix`. Add regression tests covering suffix-boundary bypass attempts (e.g., `evilethereum.org` against `*.ethereum.org`).

### Proof of Concept
1. Configure the Gateway user server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Send a request to the Gateway's user-facing path with header `Origin: https://evilethereum.org`.
3. Observe `isAllowedOrigin` returns `true` because `strings.HasSuffix("evilethereum.org", "ethereum.org")` is `true`, and the response reflects `Access-Control-Allow-Origin: https://evilethereum.org` plus permissive CORS headers, as implemented at [5](#0-4) , despite `evilethereum.org` not being a genuine subdomain of `ethereum.org`.

### Citations

**File:** core/services/gateway/network/httpserver.go (L184-209)
```go
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
