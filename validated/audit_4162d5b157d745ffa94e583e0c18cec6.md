### Title
Missing `Cache-Control: no-store` on sensitive API responses (session cookies, API tokens, key exports) allows browser-cache disclosure - ([File: core/web/router.go])

### Summary
The Chainlink node's web/API router never sets cache-prevention headers (`Cache-Control: no-store`, `Pragma: no-cache`) on any response, including responses that carry session-authentication payloads, newly generated API tokens, and exported/encrypted key material. This mirrors the CVE-2020-10096 bug class (Zammad ZAA-2020-11): confidential data is left cacheable by the browser, so an attacker with local/physical access to a workstation (no application credentials required) can recover sensitive data straight from the browser cache.

### Finding Description
`NewRouter` wires the global gin middleware stack: request-size limiter, request logger, CORS, `secureMiddleware` (TLS/HSTS), and `helmet.Default()` [1](#0-0) . The only security headers actually verified/emitted are `X-Content-Type-Options`, `X-DNS-Prefetch-Control`, `X-Frame-Options`, `Strict-Transport-Security`, `X-Download-Options`, and `X-Xss-Protection` — no `Cache-Control` or `Pragma` header is set anywhere in this chain, as confirmed by the router's own header assertion test [2](#0-1) .

Because no `no-store` directive is applied, several endpoints that return highly sensitive payloads are cacheable by the browser (and any intermediary HTTP cache) by default:
- `SessionsController.Create` returns the session-authenticated response body right after setting the session cookie, over `POST /sessions` [3](#0-2) .
- `UserController.NewAPIToken` returns a freshly generated API token in the JSON body [4](#0-3) .
- `ETHKeysController.Export` streams the exported (encrypted) key material directly in the response body via `c.Data(...)` [5](#0-4) ; the same `Export` pattern exists for CSA, OCR, OCR2, P2P, and VRF key controllers.
- OIDC token exchange responses containing role/claim confirmation and session establishment [6](#0-5) .

None of these handlers or the router pipeline set `Cache-Control: no-store, no-cache` / `Pragma: no-cache`, so a browser is free to persist these response bodies (and cookies) in its disk/memory cache per standard HTTP caching semantics.

### Impact Explanation
An attacker who obtains local access to an admin/operator's workstation (browser profile, disk cache, forensic recovery, shared machine, or a separate local process capable of reading browser cache) can recover session-authentication confirmations, freshly minted API tokens, and encrypted key-export blobs without ever authenticating to the Chainlink node's API. This is a direct confidentiality violation of secrets (API tokens, key export material) that should otherwise require valid credentials.

### Likelihood Explanation
Exploitation requires no interaction with the Chainlink node's authentication or role logic — it only requires the standard, unmodified browser caching behavior plus local/physical access to the victim's cache, exactly the threat model described in CVE-2020-10096. Because no route or middleware ever emits `Cache-Control: no-store`, every authenticated response, including one-time-sensitive payloads like key exports and new API tokens, is subject to default browser cache heuristics.

### Recommendation
Add a global (or at minimum per-authenticated-route) middleware in `NewRouter` that sets `Cache-Control: no-store, no-cache, must-revalidate` and `Pragma: no-cache` on all `/sessions`, `/v2/*` authenticated, and key-export responses, similar to how `secureMiddleware`/`helmet.Default()` are already wired in [1](#0-0) .

### Proof of Concept
1. Log into the Chainlink Operator UI, or call `POST /sessions` with valid credentials — the JSON response and `Set-Cookie: clsession=...` are cached by the browser per default HTTP caching rules since no `Cache-Control` header is present.
2. Call `POST /v2/user/token` (`NewAPIToken`) — the response body containing the plaintext API token is likewise cacheable [7](#0-6) .
3. Call `POST /v2/keys/eth/export/:address` — the encrypted key JSON returned via `c.Data` is cacheable [5](#0-4) .
4. An attacker with subsequent local access to the browser's cache directory (or via forensic tools) can extract these responses without any Chainlink credentials.

### Citations

**File:** core/web/router.go (L64-76)
```go
	engine.Use(
		otelgin.Middleware("chainlink-web-routes",
			otelgin.WithTracerProvider(otel.GetTracerProvider())),
		limits.RequestSizeLimiter(config.WebServer().HTTPMaxSize()),
		loggerFunc(app.GetLogger()),
		gin.Recovery(),
		cors,
		secureMiddleware(tls.ForceRedirect(), tls.Host(), config.Insecure().DevWebServer()),
	)
	if prometheus != nil {
		engine.Use(prometheus.Instrument())
	}
	engine.Use(helmet.Default())
```

**File:** core/web/router_test.go (L180-209)
```go
func TestRouter_GinHelmetHeaders(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, ts.URL, nil)
	require.NoError(t, err)
	res, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	for _, tt := range []struct {
		HelmetName  string
		HeaderKey   string
		HeaderValue string
	}{
		{"NoSniff", "X-Content-Type-Options", "nosniff"},
		{"DNSPrefetchControl", "X-DNS-Prefetch-Control", "off"},
		{"FrameGuard", "X-Frame-Options", "DENY"},
		{"SetHSTS", "Strict-Transport-Security", "max-age=5184000; includeSubDomains"},
		{"IENoOpen", "X-Download-Options", "noopen"},
		{"XSSFilter", "X-Xss-Protection", "1; mode=block"},
	} {
		assert.Equal(t, res.Header.Get(tt.HeaderKey), tt.HeaderValue,
			"wrong header for helmet's %s handler", tt.HelmetName)
	}
}
```

**File:** core/web/sessions_controller.go (L29-67)
```go
func (sc *SessionsController) Create(c *gin.Context) {
	defer sc.App.WakeSessionReaper()
	ctx := c.Request.Context()
	sc.App.GetLogger().Debugf("TRACE: Starting Session Creation")

	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}

	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// If the user has registered MFA tokens, then populate our session store and context
	// required for successful WebAuthn authentication
	if len(userWebAuthnTokens) > 0 {
		sr.SessionStore = sc.sessions
		sr.WebAuthnConfig = sc.App.GetWebAuthnConfiguration()
	}

	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}

	if err := saveSessionID(session, sid); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, errors.Join(errors.New("unable to save session id"), err))
		return
	}

	jsonAPIResponse(c, Session{Authenticated: true}, "session")
```

**File:** core/web/user_controller.go (L244-286)
```go
func (u *UserController) NewAPIToken(c *gin.Context) {
	ctx := c.Request.Context()
	var request clsession.ChangeAuthTokenRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to create API token"))
		return
	}
	// In order to create an API token, login validation with provided password must succeed
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
	if err != nil {
		u.App.GetAuditLogger().Audit(audit.APITokenCreateAttemptPasswordMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusUnauthorized, errors.New("incorrect password"))
		return
	}
	newToken := auth.NewToken()
	if err := u.App.AuthenticationProvider().SetAuthToken(ctx, &user, newToken); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	u.App.GetAuditLogger().Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	jsonAPIResponseWithStatus(c, newToken, "auth_token", http.StatusCreated)
}
```

**File:** core/web/eth_keys_controller.go (L240-258)
```go
func (ekc *ETHKeysController) Export(c *gin.Context) {
	defer ekc.app.GetLogger().ErrorIfFn(c.Request.Body.Close, "Error closing Export request body")

	id := c.Param("address")
	newPassword := c.Query("newpassword")

	bytes, err := ekc.app.GetKeyStore().Eth().Export(c.Request.Context(), id, newPassword)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	ekc.app.GetAuditLogger().Audit(audit.KeyExported, map[string]any{
		"type": "ethereum",
		"id":   id,
	})

	c.Data(http.StatusOK, MediaType, bytes)
}
```

**File:** core/sessions/oidcauth/oidc.go (L163-276)
```go
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

	// Begin token exchange to retrieve attested claims of authenticated user
	ctx := context.Background()
	oauth2Token, err := oi.oauth2Config.Exchange(ctx, req.Code)
	if err != nil {
		oi.lggr.Errorf("Failed to exchange token: %v", err)
		c.JSON(http.StatusInternalServerError, ExchangeTokenResponse{
			Success: false,
			Message: "OIDC exchange failed",
		})
		return
	}

	// Request token from provider for claims lookup and verification
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}

	// Verify claim and retrieve attested user id claims
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
		return
	}

	var claims map[string]any
	if err = idToken.Claims(&claims); err != nil {
		oi.lggr.Errorf("Failed to parse OIDC return claims: %v", err)
		c.String(http.StatusInternalServerError, "Failed to parse OIDC return claims")
		return
	}
	idClaims, err := oi.ExtractIDClaimValues(claims, oi.config.ClaimName())
	if err != nil {
		oi.lggr.Errorf("Failed to extract ID claims from ID token. ClaimName: '%s': error %v", oi.config.ClaimName(), err)
		c.String(http.StatusInternalServerError, "Failed to extract ID claims from claims")
		return
	}
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

	// Map the claims to a role and insert a newly created session paired with role mapping for user
	role, err := oi.IDClaimsToUserRole(
		idClaims,
		oi.config.AdminClaim(),
		oi.config.EditClaim(),
		oi.config.RunClaim(),
		oi.config.ReadClaim(),
	)
	if err != nil {
		oi.lggr.Errorf("Failed to map configured RBAC role name against received list of group claims: %v", err)
		c.String(http.StatusBadRequest, "No matching role within attested user group claims")
		return
	}

	// Save new user authenticated clSession and role to oidc_sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	clSession := clsessions.NewSession()
	_, err = oi.ds.ExecContext(
		ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		clSession.ID,
		strings.ToLower(email),
		role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		c.String(http.StatusInternalServerError, "Error creating session")
	}

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})

	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
	}

	c.JSON(http.StatusOK, ExchangeTokenResponse{
		Success: true,
	})
}
```
