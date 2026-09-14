Confirmed: `bcrypt.CompareHashAndPassword` is used with `bcrypt.DefaultCost` [1](#0-0) , which is computationally expensive (tens-to-hundreds of milliseconds), and it is only invoked when `FindUser` succeeds — giving a strong, measurable timing side-channel comparable to the Directus bug class.

### Title
User Enumeration via Login Timing Side-Channel in Local Authentication `CreateSession` - (File: core/sessions/localauth/orm.go)

### Summary
The `/sessions` login endpoint returns immediately for non-existent emails but performs an expensive bcrypt password comparison for existing emails, creating a measurable response-time difference that discloses whether an email is a registered chainlink node operator account.

### Finding Description
`SessionsController.Create` is an unauthenticated, internet-facing endpoint that forwards the raw request body into `AuthenticationProvider().CreateSession` [2](#0-1) . The underlying local-auth implementation first performs a plain (fast) SQL lookup via `FindUser`, and returns an error path immediately if no matching user row is found — without ever touching `utils.CheckPasswordHash` [3](#0-2) . Only when a user row **is** found does the code proceed to run `utils.CheckPasswordHash`, which wraps `bcrypt.CompareHashAndPassword` with `bcrypt.DefaultCost` [4](#0-3) . Bcrypt is deliberately slow (by design, tens of milliseconds at default cost), so a request for a valid email plus a wrong password takes measurably longer than a request for an email that doesn't exist at all. This is structurally identical to the reported bug class: an "existence check" is short-circuited before the constant-time/expensive protection is applied, letting response latency leak account existence. The `constantTimeEmailCompare` helper immediately following `FindUser` only protects against case/casing mismatches on an already-found user — it does nothing to equalize timing for the not-found path, since the function returns before that comparison is ever reached [5](#0-4) . The same pattern is duplicated in the LDAP and OIDC local-fallback code paths [6](#0-5) [7](#0-6) .

### Impact Explanation
An unauthenticated attacker hitting `/sessions` can enumerate valid chainlink node-operator email/admin accounts by measuring response latency, since only requests naming a real account trigger the slow bcrypt path. This enables targeted credential-stuffing/brute-force and phishing campaigns against confirmed operator accounts, and is a direct violation of user-existence confidentiality (CWE-203), mirroring the CVSS vector of the reported advisory (network, low complexity, no privileges/UI, confidentiality-only impact).

### Likelihood Explanation
Likelihood is moderate-to-high: the endpoint is unauthenticated and reachable by any network client, the timing gap is caused by an inherently slow operation (bcrypt) versus an inherently fast one (a failed/absent SQL row lookup), so the signal-to-noise ratio for a timing measurement is large and easily distinguished over the network with a modest number of samples, similar to the referenced advisory's ~500ms gap. Rate limiting exists (`TestSessions_RateLimited` shows a 429 after repeated attempts) [8](#0-7) , which raises the cost of large-scale enumeration but does not eliminate the underlying timing signal for lower-volume probing.

### Recommendation
Perform a dummy/constant-cost bcrypt comparison (against a fixed precomputed hash) whenever `FindUser` fails, so that both the "user not found" and "user found, wrong password" paths always execute a bcrypt comparison of equivalent cost before returning an error. Alternatively, always execute `CheckPasswordHash` unconditionally using either the real hash or a fixed dummy hash, and only branch on the result afterward, ensuring uniform response timing regardless of account existence. Apply the same fix to the LDAP and OIDC `localLoginFallback` implementations.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"nonexistent@example.com","password":"x"}` and measure response time — returns fast (SQL miss only, no bcrypt).
2. Send `POST /sessions` with `{"email":"<confirmed-or-guessed-valid-email>","password":"wrongpassword"}` and measure response time — takes noticeably longer due to bcrypt comparison in `utils.CheckPasswordHash`.
3. Repeating step 1/2 across many candidate emails and comparing latency distributions distinguishes existing accounts from non-existing ones, as in `TestUserController_UpdatePassword`/`TestSessionsController_Create` test flows that exercise this exact code path [9](#0-8) .

### Citations

**File:** core/utils/utils.go (L125-135)
```go
// HashPassword wraps around bcrypt.GenerateFromPassword for a friendlier API.
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes), err
}

// CheckPasswordHash wraps around bcrypt.CompareHashAndPassword for a friendlier API.
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}
```

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

**File:** core/sessions/ldapauth/ldap.go (L624-642)
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
}
```

**File:** core/sessions/oidcauth/oidc.go (L580-597)
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
}
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

**File:** core/web/sessions_controller_test.go (L22-42)
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
```
