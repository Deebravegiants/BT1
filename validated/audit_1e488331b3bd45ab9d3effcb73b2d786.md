Audit Report

## Title
Improper wildcard-origin suffix matching allows CORS origin bypass in the Gateway User HTTP server - (File: `core/services/gateway/network/httpserver.go`)

## Summary
The Gateway's `UserServerConfig` HTTP server validates CORS `Origin` headers in `isAllowedOrigin`, which supports wildcard subdomain entries like `*.example.com`. The wildcard branch strips the `*.` prefix and performs a raw `strings.HasSuffix(originHost, allowedHost)` check without requiring a dot boundary, so any domain that merely ends with the allowed suffix string (e.g. `notexample.com` or `evil-example.com` for an allowed `*.example.com`) is incorrectly treated as a trusted subdomain.

## Finding Description
Confirmed in the actual source: [1](#0-0) . The exact-host check at line 181 is correct, but the wildcard branch at lines 185-190 strips `*.` and does a bare suffix comparison with no `.` boundary requirement, so `strings.HasSuffix("notexample.com", "example.com")` evaluates true even though `notexample.com` is an entirely unrelated, attacker-registrable domain.

This function gates `handleRequest`, which reflects the origin back via `Access-Control-Allow-Origin` when `isAllowedOrigin` returns true: [2](#0-1) . This server is instantiated for the internet-facing `UserServerConfig` endpoint that unprivileged external clients call: [3](#0-2) .

The existing test suite for wildcard mismatches (`TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards`) covers scheme, port, and clearly-different-domain cases but does not test a domain that merely shares the suffix string without a proper subdomain boundary, confirming the gap is untested: [4](#0-3) .

Note: `CORSEnabled` defaults to `false` and `CORSAllowedOrigins` defaults to an empty list in the sample config, so this only manifests when an operator opts into the wildcard-origin feature — which is itself a documented, supported code path, not an out-of-scope misconfiguration, since the bug lies in the implementation of that feature. Additionally, authentication on this endpoint is via a JWT `Authorization: Bearer` header extracted from the request, not cookies, and the server does not set `Access-Control-Allow-Credentials`: [5](#0-4) . This limits — but does not eliminate — impact: it does not enable automatic credential/cookie forwarding, but it does allow an unrelated attacker-controlled origin to bypass the intended origin allowlist and have its cross-origin responses readable by browser JS for any requests it can construct (including unauthenticated gateway methods, if any), which maps to the in-scope "allowlist bypass" impact category.

## Impact Explanation
This is a genuine logic bug in the CORS origin-validation control, allowing bypass of an operator-configured origin allowlist by any domain sharing a suffix string with the intended allowed suffix. Impact is bounded by the fact that no credentials/cookies are automatically forwarded (auth uses Bearer tokens set explicitly by the calling page), so it does not directly enable session hijacking, but it does constitute an allowlist-bypass vulnerability in an internet-facing component.

## Likelihood Explanation
Requires the operator to have opted into `CORSEnabled = true` with a wildcard entry in `CORSAllowedOrigins` — a supported, documented configuration, not a misuse of the system. Given that precondition, exploitation requires only that an attacker register/control a domain sharing the suffix string and issue a browser-based cross-origin request with a crafted `Origin` header — no authentication or elevated access needed.

## Recommendation
Change the wildcard suffix check in `isAllowedOrigin` to require a dot boundary: `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`, per the code at [1](#0-0) .

## Proof of Concept
1. Start the gateway user HTTP server with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Send a POST request to the `/user` path with header `Origin: https://notexample.com`.
3. Observe `isAllowedOrigin` returns `true` and the response includes `Access-Control-Allow-Origin: https://notexample.com`, confirming the bypass, since `strings.HasSuffix("notexample.com", "example.com")` is true without a dot boundary. This can be added as a new case to `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` in `core/services/gateway/network/httpserver_test.go` asserting the CORS headers are (incorrectly) present for such an origin.

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

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```

**File:** core/services/gateway/gateway.go (L85-88)
```go
	httpServer, err := gw_net.NewHTTPServer(&cfg.UserServerConfig, connMgr.ReadyForTraffic, lggr, lf)
	if err != nil {
		return nil, err
	}
```

**File:** core/services/gateway/network/httpserver_test.go (L218-252)
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

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "http://another.valid.domain.org"                                            // http instead of https
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Methods"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Headers"))

	handler.On("ProcessRequest", mock.Anything, mock.Anything, mock.Anything).Return([]byte("response"), 200)

	origin = "http://example.gov"                                                         // port missing
	resp, respBytes = sendRequest(t, url, []byte("0123456789"), http.MethodPost, &origin) //nolint:bodyclose // sendRequest closes the body
	require.Equal(t, http.StatusOK, resp.StatusCode)
	require.Equal(t, []byte("response"), respBytes)
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Origin"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Methods"))
	require.Empty(t, resp.Header.Get("Access-Control-Allow-Headers"))
}
```
