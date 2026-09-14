Confirmed: `jsonAPIError(c, http.StatusUnauthorized, err)` in `SessionsController.Create` (`core/web/sessions_controller.go:56-60`) serializes `err.Error()` directly into the JSON response body via `models.NewJSONAPIErrorsWith(err.Error())` in `core/web/helpers.go:21-29`. The underlying `CreateSession` implementations return distinguishable error text depending on whether the account exists versus whether the password was wrong.

### Title
Username Enumeration via Distinct Login Error Messages in `SessionsController.Create` - (File: `core/web/sessions_controller.go`)

### Summary
The `/sessions` login endpoint returns different, attacker-visible error strings depending on whether the submitted email corresponds to an existing account, allowing unauthenticated enumeration of valid Chainlink node usernames — the same bug class as GHSA-38wq-6q2w-hcf9 (Rucio WebUI).

### Finding Description
`SessionsController.Create` forwards any error from `AuthenticationProvider().CreateSession` straight to the client with `jsonAPIError(c, http.StatusUnauthorized, err)` [1](#0-0) , and `jsonAPIError` embeds `err.Error()` verbatim into the JSON response body [2](#0-1) .

In the local-auth provider, `CreateSession` first calls `FindUser`; if the email doesn't exist in the `users` table, the raw SQL "no rows" error is returned immediately, whereas if the email exists but the password is wrong, the distinct string `"Invalid password"` is returned [3](#0-2) . The same divergent pattern exists in the LDAP provider's `localLoginFallback`, which emits `"invalid email"` vs `"invalid password"` [4](#0-3) , and in the OIDC provider's `localLoginFallback` with identical `"invalid email"` / `"invalid password"` strings [5](#0-4) .

This is the exact analog described in the Rucio advisory: distinguishable authentication-failure text is returned to an unauthenticated client based solely on identity existence.

### Impact Explanation
An unauthenticated attacker hitting the `/sessions` endpoint can distinguish "account does not exist" from "account exists, wrong password" responses, enabling systematic enumeration of valid node operator emails/usernames. This directly supports targeted credential stuffing or password-guessing against confirmed accounts, and undermines any expectation of account-existence confidentiality (CWE-204).

### Likelihood Explanation
High reachability: the `/sessions` endpoint is registered with only an unauthenticated rate limiter, not authentication, in `sessionRoutes` [6](#0-5) , so any unauthenticated actor can send repeated login attempts and observe the returned error text (rate limiting reduces but doesn't eliminate practical enumeration, especially across long time windows or distributed sources).

### Recommendation
Return a single generic error message (e.g., "invalid email or password") for all `CreateSession` failure paths in `core/sessions/localauth/orm.go`, `core/sessions/ldapauth/ldap.go`, and `core/sessions/oidcauth/oidc.go`, and ensure `SessionsController.Create` does not leak the underlying provider-specific error text to the client. Continue to log the detailed reason (email-not-found vs. wrong-password) internally/audit-logged only, as is already done via `auditLogger.Audit(audit.AuthLoginFailedEmail...)` and `AuthLoginFailedPassword`.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@example.com","password":"anything"}` → provider's `FindUser` fails, response body contains the raw "no rows" / user-not-found error text.
2. `POST /sessions` with `{"email":"<known-existing-email>","password":"wrongpassword"}` → response body contains `"Invalid password"` (local auth) or `"invalid password"` (LDAP/OIDC fallback).
3. Comparing the two distinct response bodies confirms whether `<known-existing-email>` is a valid account, without any authentication required.

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
