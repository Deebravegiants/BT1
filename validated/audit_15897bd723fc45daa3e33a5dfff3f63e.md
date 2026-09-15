The code confirms the claim exactly matches the submitted report: `isAllowedOrigin` in `core/services/gateway/network/httpserver.go` strips the `*.` prefix and performs a raw `strings.HasSuffix(originHost, allowedHost)` check without dot-boundary enforcement.Audit Report

## Title
CORS wildcard origin allowlist bypass via improper suffix matching (missing dot-boundary check) - (File: core/services/gateway/network/httpserver.go)

## Summary
`isAllowedOrigin` in `core/services/gateway/network/httpserver.go` validates the `Origin` header against `CORSAllowedOrigins`. For wildcard entries (`*.example.com`), it strips the `*.` prefix and performs a raw `strings.HasSuffix(originHost, allowedHost)` check with no dot-boundary enforcement, so a domain like `evil-ethereum.org` satisfies an allowlist entry meant only for `*.ethereum.org`. This is confirmed present in the code as described in the claim.

## Finding Description
`isAllowedOrigin` parses the incoming `Origin` and each configured allowed origin via `splitURL` [1](#0-0) , then for wildcard entries does:
```go
if strings.HasPrefix(allowedHost, "*.") {
    allowedHost = allowedHost[2:]
    if strings.HasSuffix(originHost, allowedHost) {
        return true
    }
}
``` [2](#0-1) 

Because `strings.HasSuffix` only checks literal character suffix equality, `evil-ethereum.org` "ends with" `ethereum.org` and would be treated as a valid subdomain of an `*.ethereum.org` wildcard entry, even though it is not actually a subdomain. A correct implementation must require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`.

If `isAllowedOrigin` returns true, `handleRequest` reflects the attacker's `Origin` into `Access-Control-Allow-Origin`: [3](#0-2) , granting the attacker's page CORS access to the gateway's HTTP endpoint, which subsequently calls `ProcessRequest` with the extracted bearer token: [4](#0-3) .

## Impact Explanation
This is a real allowlist-bypass bug matching the described root cause exactly. However, its exploitability is constrained: the resulting CORS bypass only grants an attacker-controlled origin permission to read/send cross-origin responses at the HTTP level. It does not bypass any authentication — `ProcessRequest` still requires a valid Authorization bearer token / signed request per DON handler (e.g., JWT-based auth via `jwtBasedAuth.AuthorizeRequest`, digest/tenant checks) [5](#0-4) . CORS only affects browser-enforced same-origin restrictions on responses to credentialed requests initiated by JavaScript running in a victim's browser at the bypassed origin — it does not let the attacker forge or steal secrets/tokens directly, and standard bearer-token gateway calls are not typically issued from a browser context with implicit credentials (no cookies are used; the Authorization header must be explicitly set by the calling JS, meaning the attacker page would need to already possess a valid token to benefit from the bypass, which defeats the purpose of the attack). This significantly limits real-world impact compared to a token-forging vulnerability like the CVE-2024-27932 Deno analog referenced (which allowed a Deno Deploy request-forwarding token misuse). The exploitable impact is limited to weakening origin isolation for any code specifically designed to exploit this narrow scenario.

## Likelihood Explanation
Exploitation requires: (1) operator opt-in configuration of a wildcard CORS entry (`CORSAllowedOrigins: ["https://*.example.com"]`), which is an explicit intended feature requiring administrator/operator action to enable, and (2) a scenario where a legitimate credential/token would be sent to the gateway from a page hosted on the attacker's spoofed domain — which is not a typical automatic browser behavior (unlike cookies, Authorization headers are not automatically attached). This reduces the realistic likelihood of the described full impact chain, even though the code-level suffix-matching bug itself is verified.

## Recommendation
Replace the raw `strings.HasSuffix` check with a boundary-aware comparison: require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`, so that the matched suffix must begin immediately after a dot separator, preventing arbitrary same-suffix domains from being treated as subdomains.

## Proof of Concept
1. Configure the gateway with `CORSAllowedOrigins: ["https://*.ethereum.org"]` and `CORSEnabled: true`.
2. Send an HTTP request to the gateway's configured path with header `Origin: https://evil-ethereum.org`.
3. `isAllowedOrigin` computes `allowedHost = "ethereum.org"` and evaluates `strings.HasSuffix("evil-ethereum.org", "ethereum.org")` → `true` [2](#0-1) .
4. The server responds with `Access-Control-Allow-Origin: https://evil-ethereum.org` [3](#0-2) , confirming the bypass at the CORS-header level. This can be verified as a unit test extension of the existing `TestHTTPServer_HandleRequest_CORSEnabled_FromNotAllowedOriginWildcards` test in `core/services/gateway/network/httpserver_test.go` [6](#0-5) , which currently only tests `ethereum.remix.org` (which does not share the suffix) but does not test the true bypass case of `evil-ethereum.org` / `notethereum.org`.

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

**File:** core/services/gateway/network/httpserver.go (L195-202)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
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

**File:** core/capabilities/vault/jwt_based_auth.go (L188-217)
```go
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}

	if scopeErr := enforceVaultJWTOAuthScopes(req.Method, claims.OAuthScopes); scopeErr != nil {
		v.lggr.Debugw("JWTBasedAuth OAuth scope rejected request", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "scopes", claims.OAuthScopes, "error", scopeErr)
		return nil, fmt.Errorf("invalid JWT auth token: %w", scopeErr)
	}

	if claims.TenantID == 0 {
		return nil, ErrMissingTenantID
	}
	if claims.TenantID != v.expectedTenantID {
		v.lggr.Debugw("JWT tenant id does not match job spec auth0 tenantID", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "claimsTenantID", claims.TenantID, "expectedTenantID", v.expectedTenantID)
		return nil, fmt.Errorf("%w: jwt tenant id %d expected tenant id %d", ErrJWTTenantIDJobSpecMismatch, claims.TenantID, v.expectedTenantID)
	}

	requestDigest, err := req.Digest()
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth failed to compute request digest", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "error", err)
		return nil, fmt.Errorf("failed to compute request digest: %w", err)
	}

	if !strings.EqualFold(requestDigest, claims.RequestDigest) {
		v.lggr.Debugw("JWTBasedAuth request digest mismatch", "method", req.Method, "requestID", req.ID, "orgID", claims.OrgID, "workflowOwner", claims.WorkflowOwner, "computedDigest", requestDigest, "claimedDigest", claims.RequestDigest)
		return nil, fmt.Errorf("request digest mismatch: computed=%s claimed=%s", requestDigest, claims.RequestDigest)
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
