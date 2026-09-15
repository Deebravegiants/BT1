### Title
Username Enumeration via Differentiated Login Error Messages in Local Session Authentication - (File: `core/sessions/localauth/orm.go`)

### Summary
The local authentication `CreateSession` flow returns distinct, unauthenticated-reachable error messages depending on whether the submitted email exists in the `users` table versus whether the password is merely incorrect. This lets an unauthenticated remote attacker enumerate valid Chainlink node operator/admin usernames (emails) through the `/sessions` login endpoint, the same class of bug as CVE-2019-16180 (LimeSurvey LDAP login username enumeration via distinguishable login responses).

### Finding Description
The `POST /sessions` endpoint is handled by `SessionsController.Create` [1](#0-0) , which forwards credentials to `AuthenticationProvider().CreateSession` and surfaces the returned error verbatim to the client via `jsonAPIError(c, http.StatusUnauthorized, err)` [2](#0-1) .

For the local authentication provider, `CreateSession` first looks up the user by email, and if the lookup itself fails (i.e., the email does not exist), it returns the raw database error directly: [3](#0-2) 

If the email is found but doesn't match (an edge case) it returns `"Invalid email"`, and if the password comparison fails it returns a **different** message, `"Invalid password"`: [4](#0-3) 

These three distinct outcomes — a raw "no rows" style DB error for a nonexistent email, `"Invalid email"`, or `"Invalid password"` — are each propagated unmodified into the HTTP 401 response body, allowing an attacker to distinguish "this email is not registered" from "this email is registered but the password is wrong."

This mirrors the CVE-2019-16180 bug class: the login form gives an unprivileged, unauthenticated attacker a reliable oracle to enumerate valid account emails without needing valid credentials.

Note: the OIDC (`core/sessions/oidcauth/oidc.go`, lines 580-597) and LDAP (`core/sessions/ldapauth/ldap.go`, lines 622-642) `localLoginFallback` functions contain an analogous email/password split, but only local authentication's primary `CreateSession` path additionally leaks the raw "no rows" database error prior to any generic message, making it the strongest and most directly reachable analog.

### Impact Explanation
An unauthenticated network attacker can enumerate valid operator emails registered on a Chainlink node's Operator UI/API by observing whether the response is a raw SQL "not found" style error versus `"Invalid password"`. Username enumeration is a stepping stone for targeted credential-stuffing or brute-force attacks against the node's admin/operator accounts, which control job management and key operations.

### Likelihood Explanation
The endpoint is internet-facing (`/sessions`, unauthenticated by design) and reachable without any prior access [5](#0-4) . The only mitigating control is the configured unauthenticated rate limit (`WebServer.RateLimit.Unauthenticated = 5` per `UnauthenticatedPeriod = '20s'`) [6](#0-5) , confirmed enforced by `TestSessions_RateLimited` [7](#0-6) . Rate limiting slows but does not prevent enumeration; a patient attacker can still iterate through a candidate email list over time.

### Recommendation
Return a single generic error (e.g., `"invalid email or password"`) for all failure branches in `orm.CreateSession` — nonexistent email, DB lookup error, and password mismatch — instead of surfacing distinct messages or raw database errors, and apply the same normalization to the equivalent `localLoginFallback` paths in the OIDC and LDAP authenticators.

### Proof of Concept
1. `POST /sessions` with `{"email":"doesnotexist@example.com","password":"x"}` → response body contains a raw DB "no rows" error message, confirming the email is not registered.
2. `POST /sessions` with `{"email":"knownadmin@example.com","password":"wrong"}` → response body contains `"Invalid password"`, confirming the email IS registered.
3. Comparing the two distinguishable responses over a list of candidate emails lets an attacker enumerate valid node operator accounts without needing valid credentials, matching the CVE-2019-16180 bug class of login-form-based username enumeration. [8](#0-7) [2](#0-1)

### Citations

**File:** core/web/sessions_controller.go (L29-60)
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
```

**File:** core/sessions/localauth/orm.go (L144-162)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")

	// Do email and password check first to prevent extra database look up
	// for MFA tokens leaking if an account has MFA tokens or not.
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```

**File:** core/web/router.go (L86-90)
```go

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
```

**File:** core/config/docs/core.toml (L278-281)
```text
# Unauthenticated defines the threshold to which authenticated requests get limited. More than this many unauthenticated requests per `UnAuthenticatedRateLimitPeriod` will be rejected.
Unauthenticated = 5 # Default
# UnauthenticatedPeriod defines the period to which unauthenticated requests get limited.
UnauthenticatedPeriod = '20s' # Default
```

**File:** core/web/router_test.go (L127-156)
```go
func TestSessions_RateLimited(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	input := `{"email":"brute@force.com", "password": "wrongpassword"}`

	for range 5 {
		request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
		require.NoError(t, err)

		resp, err := client.Do(request)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	}

	request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
	require.NoError(t, err)

	resp, err := client.Do(request)
	require.NoError(t, err)
	assert.Equal(t, 429, resp.StatusCode)
}
```
