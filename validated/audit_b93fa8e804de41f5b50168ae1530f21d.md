## Finding

The chainlink node's `/sessions` login endpoint leaks whether a submitted email corresponds to a valid account, because the underlying `CreateSession` implementation returns a *different, raw error* when the account does not exist versus when the account exists but the password is wrong — and that raw error message is placed directly into the HTTP response body.

### Title
Account enumeration via distinguishable error messages on `/sessions` login endpoint - (File: `core/sessions/localauth/orm.go`)

### Summary
The local authentication provider's `CreateSession` function looks up the user by email first. If no user with that email exists, it returns the raw database error (`sql.ErrNoRows`, rendered as `"sql: no rows in result set"`) immediately. If the user does exist but the password is wrong, it instead returns the distinct string `"Invalid password"`. Both of these errors are serialized verbatim into the JSON response by the `sessions_controller.go` handler, allowing an unauthenticated caller to distinguish "no such account" from "account exists, wrong password" by inspecting the response body — the exact bug class described in GHSA-7vwg-39h8-8qp8 for eZ Platform's `/user/sessions` endpoint.

### Finding Description
`SessionsController.Create` accepts unauthenticated POST requests to `/sessions` and forwards them to `AuthenticationProvider().CreateSession`: [1](#0-0) 

On error, it writes the error directly into the JSON API response body via `jsonAPIError`, which serializes `err.Error()` as the `detail` field: [2](#0-1) 

The local ORM's `CreateSession` first calls `FindUser`, and if it fails (e.g., email not found) returns that raw error immediately — before doing any password/email comparison: [3](#0-2) 

`FindUser`/`findUser` performs a bare `SELECT ... WHERE lower(email) = lower($1)` and returns whatever `sqlx` produces (typically `sql.ErrNoRows`) when no row matches: [4](#0-3) 

So for a non-existent email, the client receives an error like `"sql: no rows in result set"`, whereas for a valid email with a wrong password the client receives `"Invalid password"`. The code even has a comment acknowledging the importance of not leaking account-specific info (MFA presence) via a similarly-shaped check, but that protection was applied only to the *password/email* comparison step, not to the initial `FindUser` lookup that precedes it: [5](#0-4) 

The LDAP and OIDC authentication providers do not have this exact issue in their primary path since they attempt an LDAP/OIDC bind first, but their `localLoginFallback` functions exhibit the analogous pattern (raw `err` from `GetContext` returned on no-such-user, vs. `"invalid password"` for existing accounts): [6](#0-5) [7](#0-6) 

### Impact Explanation
An unauthenticated remote attacker sending POST requests to `/sessions` can determine whether a given email address is a registered chainlink node API user by observing the distinct error text in the JSON response ("no rows in result set"-style error vs. "Invalid password"). This is a direct account-enumeration primitive against the node's administrative API user base, which can be used to target subsequent credential-stuffing or brute-force attacks (mitigated only by the existing rate limiter) against confirmed-valid accounts.

### Likelihood Explanation
Reaching this code path requires only an unauthenticated HTTP POST to `/sessions` with an arbitrary email/password pair — this route is explicitly registered in the unauthenticated route group: [8](#0-7) 
No special privileges or prior access are needed, making likelihood high for any node with the HTTP API exposed.

### Recommendation
Normalize the error returned by `CreateSession` (and the LDAP/OIDC `localLoginFallback` equivalents) so that "user not found" and "invalid password" produce an identical, generic error (e.g., `"invalid email or password"`) with equalized response timing, mirroring the fix applied upstream for GHSA-7vwg-39h8-8qp8. Avoid ever surfacing raw database errors (e.g., `sql.ErrNoRows`) through `jsonAPIError`.

### Proof of Concept
1. POST `{"email":"nonexistent@test.com","password":"x"}` to `/sessions` → response body contains raw SQL error such as `"sql: no rows in result set"`.
2. POST `{"email":"<valid-registered-email>","password":"wrongpassword"}` to `/sessions` → response body contains `"Invalid password"`.
3. Comparing the two distinct error strings across repeated requests for different candidate emails allows an attacker to enumerate valid accounts. [9](#0-8)

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

**File:** core/web/helpers.go (L19-29)
```go
// jsonAPIError adds an error to the gin context and sets
// the JSON value of errors.
func jsonAPIError(c *gin.Context, statusCode int, err error) {
	_ = c.Error(err).SetType(gin.ErrorTypePublic)
	var jsonErr *models.JSONAPIErrors
	if errors.As(err, &jsonErr) {
		c.JSON(statusCode, jsonErr)
		return
	}
	c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))
}
```

**File:** core/sessions/localauth/orm.go (L43-58)
```go
// FindUser will attempt to return an API user by email.
func (o *orm) FindUser(ctx context.Context, email string) (sessions.User, error) {
	return o.findUser(ctx, email)
}

// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}

func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
	return
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

**File:** core/sessions/ldapauth/ldap.go (L624-641)
```go
func (l *ldapAuthenticator) localLoginFallback(ctx context.Context, sr sessions.SessionRequest) (sessions.User, error) {
	var user sessions.User
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err := l.ds.GetContext(ctx, &user, sql, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		l.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		l.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
```

**File:** core/sessions/oidcauth/oidc.go (L580-596)
```go
func (oi *oidcAuthenticator) localLoginFallback(ctx context.Context, sr clsessions.SessionRequest) (clsessions.User, error) {
	var user clsessions.User
	err := oi.ds.GetContext(ctx, &user, SQLSelectUserbyEmail, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
```

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}
```

**File:** core/web/sessions_controller_test.go (L22-80)
```go
func TestSessionsController_Create(t *testing.T) {
	t.Parallel()
	ctx := t.Context()

	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	user := cltest.MustRandomUser(t)
	require.NoError(t, app.AuthenticationProvider().CreateUser(ctx, &user))

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	tests := []struct {
		name        string
		email       string
		password    string
		wantSession bool
	}{
		{"incorrect pwd", user.Email, "incorrect", false},
		{"incorrect email", "incorrect@test.net", cltest.Password, false},
		{"correct", user.Email, cltest.Password, true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			ctx := t.Context()
			body := fmt.Sprintf(`{"email":"%s","password":"%s"}`, test.email, test.password)
			request, err := http.NewRequestWithContext(ctx, http.MethodPost, app.Server.URL+"/sessions", bytes.NewBufferString(body))
			require.NoError(t, err)
			resp, err := client.Do(request)
			require.NoError(t, err)
			defer func() { require.NoError(t, resp.Body.Close()) }()

			if test.wantSession {
				require.Equal(t, http.StatusOK, resp.StatusCode)

				cookies := resp.Cookies()
				sessionCookie := web.FindSessionCookie(cookies)
				require.NotNil(t, sessionCookie)

				decrypted, err := cltest.DecodeSessionCookie(sessionCookie.Value)
				require.NoError(t, err)
				user, err := app.AuthenticationProvider().AuthorizedUserWithSession(ctx, decrypted)
				require.NoError(t, err)
				assert.Equal(t, test.email, user.Email)

				b, err := io.ReadAll(resp.Body)
				require.NoError(t, err)
				assert.Contains(t, string(b), `"attributes":{"authenticated":true}`)
			} else {
				require.GreaterOrEqual(t, resp.StatusCode, 400, "Should not be able to create session")
				// Ignore fixture session
				sessions, err := app.AuthenticationProvider().Sessions(ctx, 1, 2)
				require.NoError(t, err)
				assert.Empty(t, sessions)
			}
		})
	}
```
