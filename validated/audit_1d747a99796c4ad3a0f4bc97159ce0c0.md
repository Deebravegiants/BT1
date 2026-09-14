## Analysis Result

I found a valid analog. Chainlink's local session login endpoint returns distinct, content-differentiated error messages depending on whether the submitted email exists in the `users` table versus exists but with a wrong password — the same class of bug as CVE-2023-34243 (distinguishable response reveals whether a valid account was found).

### Title
Username enumeration via distinct login error messages on `/sessions` endpoint - ([File: core/sessions/localauth/orm.go])

### Summary
The local authentication `CreateSession` flow returns the raw database error (`sql.ErrNoRows`, i.e. "sql: no rows in result set") when the submitted email does not match any user, but returns a distinct application error `"Invalid password"` when the email matches an existing user but the password is wrong. Both errors are propagated verbatim to the HTTP client in the JSON API error body, allowing an unauthenticated attacker to enumerate valid TGS-node admin usernames/emails, analogous to the Windows-username disclosure described in CVE-2023-34243.

### Finding Description
`SessionsController.Create` calls `AuthenticationProvider().CreateSession(ctx, sr)` and on error passes the raw `err` straight to `jsonAPIError`, which serializes `err.Error()` into the JSON response body: [1](#0-0) [2](#0-1) 

In the local ORM's `CreateSession`, the very first step looks up the user by email. If no row is found, the raw driver error is returned unmodified: [3](#0-2) [4](#0-3) 

If the email *does* exist but the password check fails, a distinctly different, hard-coded message `"Invalid password"` is returned instead: [5](#0-4) 

The same pattern (a generic “no such row” error for a missing account vs. an explicit `"invalid password"`/`"invalid email"` message for existing accounts) is repeated in the LDAP and OIDC local-fallback code paths as well: [6](#0-5) [7](#0-6) 

The router wires this endpoint up as unauthenticated (only rate-limited), meaning any network client can probe it: [8](#0-7) 

### Impact Explanation
An unauthenticated attacker can distinguish "no such account" from "account exists, wrong password" purely from response body content (not just status code, since both return 401/error status but with different `errors[].detail` text). This allows enumeration of valid Chainlink node admin/API user emails, which is a precursor to targeted credential-stuffing or brute-force attacks against the TGS-equivalent Chainlink node UI/API — directly matching the "cross-user response confusion" / authentication-bypass-adjacent information disclosure class called out in the CVE.

### Likelihood Explanation
High likelihood of exploitation: the endpoint (`POST /sessions`) is reachable pre-authentication by design, rate limiting is the only mitigation (`rl.UnauthenticatedPeriod()`/`rl.Unauthenticated()`), and the distinguishing information is present in every failed login response with no extra timing or side channel required — a simple scripted probe against a candidate email list suffices. [9](#0-8) 

### Recommendation
Normalize all login failure responses (missing user, wrong password, missing/failed MFA) in `orm.CreateSession` (and the LDAP/OIDC equivalents) to a single generic message (e.g., `"invalid email or password"`) with the same HTTP status code, and avoid returning raw database errors (`sql.ErrNoRows`) to the client at all — wrap `FindUser` failures before returning from `CreateSession`.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@x.com","password":"anything"}` → response body contains `sql: no rows in result set` (or similar raw DB error) via `jsonAPIError`.
2. `POST /sessions` with `{"email":"<known-valid-admin-email>","password":"wrongpassword"}` → response body contains `"Invalid password"`.
3. An attacker distinguishes (1) vs (2) across a list of candidate emails to enumerate valid registered users, exactly as in CVE-2023-34243's Windows-username disclosure. [10](#0-9)

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/web/helpers.go (L21-29)
```go
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

**File:** core/sessions/localauth/orm.go (L55-59)
```go
func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
	return
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

**File:** core/web/router.go (L207-217)
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
```

**File:** core/web/sessions_controller_test.go (L33-43)
```go
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
