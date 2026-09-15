## Analysis

I found no reachable analog to the *mobile-app SSO callback theft* itself (Chainlink's OIDC token-exchange flow at [1](#0-0)  validates a server-side session-bound `state` parameter and performs the code exchange itself, so there's no analogous "relay redirect through an untrusted client" primitive). However, while investigating the internet-facing gateway's origin/allowlist handling (a category explicitly in scope), I found a genuine origin-allowlist bypass in the CORS validation logic.

### Title
CORS origin allowlist bypass via unanchored domain-suffix matching in gateway HTTP server - ([File: core/services/gateway/network/httpserver.go])

### Summary
The Chainlink Gateway's public HTTP server validates the `Origin` header against a configured allowlist (`CORSAllowedOrigins`) before reflecting it back in `Access-Control-Allow-Origin`. The wildcard-matching logic uses an unanchored string suffix check instead of a proper subdomain boundary check, allowing any attacker-registered domain that merely *ends with* the allowed domain string (not a real subdomain of it) to be treated as trusted.

### Finding Description
`isAllowedOrigin` strips the `*.` prefix from a configured wildcard entry and then checks `strings.HasSuffix(originHost, allowedHost)` with no requirement that the preceding character be a literal `.`: [2](#0-1) 

Given an allowed origin pattern like `https://*.example.com` (`allowedHost = "example.com"`), an attacker who registers and controls the completely independent, unrelated domain `xexample.com` (a valid public second-level domain, no relationship to `example.com`'s owner) will pass the check, because `"xexample.com"` literally ends with the substring `"example.com"`. The same applies to hyphenated look-alikes such as `attacker-example.com`. This is the classic "suffix-without-dot-boundary" allowlist bug.

This function gates the CORS response in the request path of the gateway's public-facing HTTP handler: [3](#0-2) 

Any unauthenticated client can trigger this simply by sending an HTTP request with a crafted `Origin` header to the gateway's public endpoint.

### Impact Explanation
When the crafted origin matches, the server reflects it via `Access-Control-Allow-Origin`, effectively telling browsers that the attacker-controlled origin is a trusted first-party client of the gateway. A page hosted on the attacker's confusable domain can then issue cross-origin requests to the gateway and have the JSON response (which may include results from gateway/vault handlers) read by attacker JavaScript, defeating the intended origin allowlist. This maps to the "allowlist bypass" impact class for the internet-facing gateway.

### Likelihood Explanation
Exploitation only requires: (1) the operator configures a wildcard CORS entry (`*.<domain>`), and (2) an attacker registers any public domain that happens to end with that domain string (e.g., `xexample.com`, `attacker-example.com`). No privileged access or credentials are required to send the crafted `Origin` header; the check is exercised on every request handled by `handleRequest`.

### Recommendation
Fix `isAllowedOrigin` to require the character immediately preceding the suffix match to be a literal `.` (proper subdomain boundary), e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // ".example.com"
    if originHost == suffix[1:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```

### Proof of Concept
1. Configure gateway with `CORSAllowedOrigins = ["https://*.example.com"]`.
2. Attacker registers `https://xexample.com` (or `https://attacker-example.com`) and hosts a page there.
3. Attacker's page issues `fetch('https://gateway-host/endpoint', {method:'POST', ...})` with `Origin: https://xexample.com`.
4. Server responds with `Access-Control-Allow-Origin: https://xexample.com`, matching test pattern behavior shown in [4](#0-3)  — the browser allows the attacker script to read the response. [5](#0-4)

### Citations

**File:** core/sessions/oidcauth/oidc.go (L147-184)
```go
func (oi *oidcAuthenticator) handleSignIn(c *gin.Context) {
	// generate state and store on session
	state := oi.generateState()
	session := sessions.Default(c)
	session.Set("state", state)
	err := session.Save()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save session"})
		return
	}

	// redirect to provider
	url := oi.oauth2Config.AuthCodeURL(state, oauth2.AccessTypeOffline)
	c.Redirect(http.StatusFound, url)
}

func (oi *oidcAuthenticator) handleTokenExchange(c *gin.Context) {
	// parse and validate the incoming JSON request
	var req ExchangeTokenRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid request: " + err.Error(),
		})
		return
	}

	// check state matches stored value on the session
	ginSession := sessions.Default(c)
	storedState := ginSession.Get("state")
	if storedState == nil || req.State != storedState.(string) {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid state parameter",
		})
		return
	}
	ginSession.Delete("state")
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
