This confirms the analog. `jsonAPIError` serializes `err.Error()` directly into the JSON API response body sent back to the caller, so whatever error string `CreateSession` returns is exposed to the unauthenticated client.

### Title
Unauthenticated `/sessions` login endpoint leaks account-existence via differential error messages - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated node login endpoint `POST /sessions`, handled by `SessionsController.Create`, forwards whatever error `AuthenticationProvider().CreateSession` returns straight into the HTTP JSON response body via `jsonAPIError`, without normalizing the message. `CreateSession` in the local-auth ORM (used when LDAP/OIDC is not configured) returns distinctly different, human-readable error strings depending on whether the submitted email exists in the `users` table or not, and if it exists, whether the password was wrong. This lets an unauthenticated caller enumerate valid node admin/API-user email addresses, the same bug class as CVE-2025-30150 (Shopware store-api account enumeration via differing error text).

### Finding Description
`SessionsController.Create` binds the request and calls the authentication provider, then passes any returned error verbatim to `jsonAPIError`, which serializes `err.Error()` into the JSON response body: [1](#0-0) [2](#0-1) 

The local-auth `CreateSession` implementation first looks up the user by email with `FindUser`, which returns the raw SQL error (effectively `sql.ErrNoRows`) if no such user exists, and returns that immediately: [3](#0-2) 

If the user is found but a subsequent (always-true, since `FindUser` already matched the email) email comparison or password check fails, it returns distinctly worded errors `"Invalid email"` / `"Invalid password"`: [4](#0-3) 

The same pattern (distinct `"invalid email"` vs `"invalid password"` messages, plus a separate not-found path) exists in the OIDC and LDAP local-login fallback authenticators: [5](#0-4) [6](#0-5) 

Because the two failure paths ("no user found" → SQL not-found error text vs "user found, wrong password" → `"Invalid password"`) produce different response bodies, an unauthenticated attacker submitting `email` guesses to `/sessions` can distinguish valid registered emails from invalid ones purely from the JSON error text/shape returned, without needing timing analysis.

### Impact Explanation
This is an account-enumeration oracle on a node's admin/API user login endpoint. An attacker with network access to the Operator UI/API (`/sessions`) can determine which email addresses correspond to real Chainlink node operator/admin accounts, aiding targeted credential-stuffing, phishing, or brute-force attacks against those confirmed accounts. It does not by itself grant authentication bypass or fund movement, matching the "Medium"/CWE-204 (Observable Response Discrepancy) classification of the reference advisory. Note that this endpoint is rate-limited (`TestSessions_RateLimited` in `core/web/router_test.go` shows 429 after 5 attempts), which somewhat mitigates but does not eliminate the enumeration capability since the discrepancy is present on every response, not just after many attempts. [7](#0-6) 

### Likelihood Explanation
Reachable by an unprivileged, unauthenticated network client — no credentials or prior access are required to hit `POST /sessions`; the endpoint is registered outside the authenticated route group. This makes the discrepancy trivially observable by any external client that can send `{"email":..., "password":...}` requests, subject to the existing per-IP rate limiting.

### Recommendation
Normalize all `CreateSession` (and local-login fallback) failure paths — user-not-found, email-mismatch, and wrong-password — into a single generic error (e.g., `"invalid credentials"`) before it is ever surfaced through `jsonAPIError`, and ensure the same generic message/timing profile is used regardless of whether the email exists. Apply this consistently across `core/sessions/localauth/orm.go`, `core/sessions/oidcauth/oidc.go`, and `core/sessions/ldapauth/ldap.go` local-login fallback paths.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@example.com","password":"x"}` → response body contains the raw SQL "no rows" style error surfaced via `jsonAPIError`/`c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))`.
2. `POST /sessions` with `{"email":"<real-admin-email>","password":"wrongpassword"}` → response body instead contains `"Invalid password"` (from `core/sessions/localauth/orm.go` line 161).
3. Comparing the two distinct response bodies for the same HTTP status code (`401 Unauthorized`) lets the attacker confirm `<real-admin-email>` is a registered account, exactly as in the Shopware `recovery-password` oracle described in GHSA-hh7j-6x3q-f52h.

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
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

**File:** core/sessions/localauth/orm.go (L144-148)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
```

**File:** core/sessions/localauth/orm.go (L152-162)
```go
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
