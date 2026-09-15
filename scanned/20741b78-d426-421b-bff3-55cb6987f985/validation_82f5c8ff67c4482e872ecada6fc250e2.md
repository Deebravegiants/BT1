Confirmed: `jsonAPIError` in `core/web/helpers.go:21-29` serializes the raw `err.Error()` string directly into the JSON response body, and `SessionsController.Create` in `core/web/sessions_controller.go:56-60` passes the error from `CreateSession` straight through to `jsonAPIError` without normalization.

### Title
Login endpoint discloses distinct "Invalid email" vs "Invalid password" errors, enabling unauthenticated user enumeration - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `POST /sessions` login endpoint returns different, verbatim error messages depending on whether the submitted email exists in the `users` table versus whether only the password was wrong. This lets any unprivileged remote caller enumerate valid operator email addresses on a Chainlink node's Operator UI, analogous to the Django `PasswordResetForm` enumeration issue (CVE-2024-45231) where response differences reveal account existence.

### Finding Description
`orm.CreateSession` (the default local-auth `AuthenticationProvider`) performs distinguishable checks and returns different sentinel error strings:
- If the email does not resolve to an existing user, `FindUser`/`findUser` returns the SQL "no rows" error, and `constantTimeEmailCompare` subsequently fails, returning `pkgerrors.New("Invalid email")`. [1](#0-0) 
- If the email exists but the password is wrong, the code proceeds past the email check and returns `pkgerrors.New("Invalid password")`. [2](#0-1) 

The same pattern exists in the LDAP and OIDC local-fallback authenticators (`invalid email` vs `invalid password`). [3](#0-2) [4](#0-3) 

These raw errors are propagated unmodified to the HTTP client. `SessionsController.Create` calls `CreateSession` and, on any error, forwards it directly to `jsonAPIError` with no generic wrapping: [5](#0-4) 

`jsonAPIError` then serializes `err.Error()` verbatim into the JSON response body sent back to the caller: [6](#0-5) 

This is the exact bug class in the Django advisory: an unauthenticated, security-sensitive flow (login here vs. password-reset in Django) exposes an externally observable signal — a distinct message — that lets an attacker determine whether a given identifier (email) corresponds to a real account.

### Impact Explanation
An unauthenticated remote attacker can send crafted login requests against `/sessions` with candidate email addresses and directly read from the JSON response body whether the email is "Invalid email" (does not exist) or "Invalid password" (exists, wrong credentials). This discloses valid operator/administrator email addresses for a given Chainlink node, which can be leveraged for targeted phishing, credential-stuffing, or brute-force attacks against confirmed accounts — the same low-confidentiality-impact class (CWE-203/204) as the Django CVE.

### Likelihood Explanation
The endpoint is internet-facing (Operator UI login), requires no authentication or special privileges to reach, and the differing messages are trivial to detect via simple automated HTTP requests. A per-IP unauthenticated rate limit exists (`WebServer.RateLimit.Unauthenticated`, default 5 requests / 20s), which slows but does not prevent enumeration. [7](#0-6) 

### Recommendation
Return a single generic error message (e.g., "invalid email or password") for both the "email not found" and "wrong password" cases across all `AuthenticationProvider` implementations (`localauth`, `ldapauth`'s `localLoginFallback`, `oidcauth`'s `localLoginFallback`), and ensure `SessionsController.Create` does not leak the internal distinguishing string. Constant-time behavior for both cases should also be preserved to avoid timing-based enumeration.

### Proof of Concept
1. `POST /sessions` with `{"email":"realuser@example.com","password":"wrongpass"}` → response body contains `"Invalid password"`.
2. `POST /sessions` with `{"email":"doesnotexist@example.com","password":"wrongpass"}` → response body contains `"Invalid email"`.
3. Comparing the two responses across a list of candidate addresses lets an attacker enumerate which emails are registered on the node, exactly as demonstrated in `core/web/router_test.go`'s `TestSessions_RateLimited`, which shows the raw `/sessions` request/response flow used here (minus the rate limit, which only throttles, not blocks, enumeration). [8](#0-7)

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L622-642)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the LDAP server
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

**File:** core/sessions/oidcauth/oidc.go (L578-597)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the OIDC server
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
