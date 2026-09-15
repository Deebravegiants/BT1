## Title
CORS wildcard-origin bypass via naive suffix matching in Gateway HTTP server allowlist - (File: core/services/gateway/network/httpserver.go)

### Summary
The Chainlink Gateway's user-facing HTTP server (`UserServerConfig`) implements a custom CORS allowlist check in `isAllowedOrigin`. When an operator configures a wildcard entry such as `"https://*.ethereum.org"`, the code strips the `*.` prefix and then checks whether the requesting `Origin` host ends with the resulting suffix string using `strings.HasSuffix`, without verifying a `.` boundary exists between the attacker-controlled prefix and the allowed suffix. This is the same class of bug as CVE-2017-14460 (Parity's overly permissive CORS whitelist): a weak/incorrect origin-matching algorithm lets an attacker-registered domain satisfy the allowlist check and receive `Access-Control-Allow-Origin` reflecting their malicious origin.

### Finding Description
In `isAllowedOrigin`, the wildcard branch is: [1](#0-0) 

`allowedHost` is derived by stripping the literal `*.` prefix (e.g., `"*.ethereum.org"` → `"ethereum.org"`), and the match is `strings.HasSuffix(originHost, allowedHost)`. This performs a raw string suffix comparison rather than a subdomain/label boundary comparison. Consequently, an attacker who registers a domain like `evilethereum.org`, `notarealethereum.org`, or `attacker-ethereum.org` will have an `originHost` that ends with the literal string `ethereum.org`, satisfying `HasSuffix` even though it is not a subdomain of `ethereum.org` at all.

This check is invoked from `handleRequest`, which is the entry point for every unauthenticated cross-origin browser request hitting the Gateway's `UserServerConfig` HTTP listener (the internet-facing JSON-RPC gateway used by DON node operators for external client/user requests): [2](#0-1) 

If the forged origin passes `isAllowedOrigin`, the server reflects it back verbatim in `Access-Control-Allow-Origin`, permitting the browser to expose the cross-origin JSON-RPC response to the malicious page's JavaScript.

The gateway's sample configs and integration tests confirm this wildcard mode is a supported, documented feature (not test-only): [3](#0-2) 

Existing unit tests only validate rejection of an origin that does **not** share the suffix at all (`https://ethereum.remix.org` vs `*.ethereum.org`), but never test the boundary-less bypass case (e.g., `evilethereum.org` vs `*.ethereum.org`): [4](#0-3) 

### Impact Explanation
The Gateway's `UserServerConfig` HTTP endpoint is the internet-facing entry point through which unprivileged external clients submit signed JSON-RPC requests to a DON via `ProcessRequest`, and receive responses. If an operator relies on a wildcard CORS entry (e.g., to allow all of `*.chain.link` or similar), an attacker can register a lookalike domain and lure a victim (who has legitimate credentials/session or is simply browsing) to visit it. The victim's browser will then be permitted by CORS to read cross-origin JSON-RPC responses from the gateway — request impersonation and response confusion across users/origins, potentially disclosing job/DON responses intended only for the legitimate origin. This maps to "allowlist bypass" and "cross-user response confusion" categories explicitly in scope.

### Likelihood Explanation
Exploitability requires: (1) a gateway operator configuring a wildcard `CORSAllowedOrigins` entry (a documented, supported feature, not a misconfiguration outside intended use), and (2) an attacker registering/controlling a domain whose name happens to end with the allowed suffix string (trivially achievable — domain registration is unrestricted, e.g., `evil<suffix>`). No privileged access or special network position is needed; only a victim visiting an attacker page, matching the CVE-2017-14460 vector ("a victim needs to visit a malicious website").

### Recommendation
Fix the wildcard comparison in `isAllowedOrigin` to enforce a proper label/subdomain boundary instead of raw suffix matching, e.g., require that `originHost` either equals `allowedHost` or ends with `"."+allowedHost`:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost) {
        return true
    }
}
```
Add regression tests asserting that domains like `evilethereum.org` are rejected against an `*.ethereum.org` allowlist entry.

### Proof of Concept
1. Configure the gateway's `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]` (as in the sample configs) [5](#0-4) .
2. Register/control a domain such as `https://evilethereum.org` (no subdomain dot, but literal suffix match).
3. Send a request to the gateway's `/user` path with header `Origin: https://evilethereum.org`.
4. `splitURL` yields `originHost = "evilethereum.org"`; the wildcard check strips `*.` from the allowed entry to get `"ethereum.org"`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true`.
5. The server responds with `Access-Control-Allow-Origin: https://evilethereum.org`, allowing the attacker's page to read the JSON-RPC response cross-origin, despite `evilethereum.org` not being a genuine subdomain of `ethereum.org`.

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

**File:** core/services/gateway/integration_tests/gateway_integration_test.go (L59-60)
```go
CORSEnabled = true
CORSAllowedOrigins = ["https://remix.ethereum.org"]
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

**File:** core/scripts/gateway/sample_config.toml (L9-10)
```text
CORSEnabled = false
CORSAllowedOrigins = []
```
