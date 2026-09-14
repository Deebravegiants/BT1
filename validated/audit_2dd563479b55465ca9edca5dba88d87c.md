Based on my investigation, this is a valid analog vulnerability.

### Title
Unauthenticated `/sessions` login endpoint reveals whether an email address is registered via differing error responses - ([File: core/web/sessions_controller.go])

### Summary
The Lemmy advisory describes an unauthenticated endpoint that leaks account existence by returning different responses for registered vs. unregistered email addresses. Chainlink's unauthenticated session-creation endpoint (`POST /sessions`) exhibits the same class of bug: it returns distinguishable error content depending on whether the submitted email exists in the `users` table, allowing anonymous email/account enumeration.

### Finding Description
`sessionRoutes` mounts `SessionsController.Create` on an unauthenticated route group, only gated by a generic rate limiter, not any anti-enumeration control: [1](#0-0) 

`SessionsController.Create` calls `AuthenticationProvider().CreateSession`, and on error returns the raw underlying error directly into the JSON response body via `jsonAPIError`: [2](#0-1) 

`jsonAPIError` serializes `err.Error()` straight into the HTTP response: [3](#0-2) 

The local authentication provider's `CreateSession` first looks up the user by email with `FindUser`, and if the account doesn't exist, that lookup error (a bare SQL error, e.g. `sql: no rows in result set`) is returned immediately and unchanged. If the account exists but the password is wrong, a distinctly different message, `"Invalid password"`, is returned instead: [4](#0-3) 

`FindUser`/`findUser` performs the raw SQL lookup that produces this distinguishable error for missing accounts: [5](#0-4) 

The OIDC authentication provider's local-admin fallback path has the same pattern, differentiating "no such user" (raw lookup error) from `"invalid email"` from `"invalid password"`: [6](#0-5) 

This is structurally identical to the Lemmy bug: an unauthenticated endpoint (`/sessions`, analogous to `resend_verification_email`) that performs a lookup-by-email and forwards the lookup outcome/error to the caller instead of normalizing all failure paths to one indistinguishable response.

### Impact Explanation
An unauthenticated attacker can submit candidate email addresses to `/sessions` and distinguish "no such account" (raw SQL/database error text) from "account exists but wrong password" (`"Invalid password"`) or from LDAP/OIDC-specific messages (`"invalid email"`, `"user not active"`, `"unable to log in with LDAP server..."`). This enables enumeration of registered Chainlink node admin/API user email addresses without credentials, which can be used to target subsequent password-guessing, phishing, or social-engineering attacks against known valid accounts. It does not by itself grant authentication bypass or fund movement, matching the Medium severity of the analogous Lemmy issue.

### Likelihood Explanation
Likelihood is high: the endpoint is unauthenticated by design (`unauth.POST("/sessions", sc.Create)`), gated only by a generic IP-based rate limiter shared with other unauthenticated routes rather than any enumeration-specific throttling, and the error text differs deterministically based on account existence, making automated probing straightforward.

### Recommendation
Normalize all failure paths in `CreateSession`/`Create` handler so that "user not found," "invalid email," and "invalid password" produce an identical generic message and status code (e.g., always `"invalid credentials"` with `401`), mirroring the safer pattern already used elsewhere for password-reset-style flows. Avoid returning raw lookup errors (e.g., `sql.ErrNoRows` text) directly to the client via `jsonAPIError`, and apply constant-time/normalized handling across `localauth`, `ldapauth`, and `oidcauth` providers' login paths.

### Proof of Concept
1. Send `POST /sessions` with `{"email": "known-admin@example.com", "password": "wrongpass"}` — observe response body contains `"Invalid password"`.
2. Send `POST /sessions` with `{"email": "doesnotexist@example.com", "password": "wrongpass"}` — observe response body contains a different message derived from the raw database lookup error (e.g., `sql: no rows in result set`), confirming the responses are distinguishable and allow email enumeration against the unauthenticated endpoint.

### Citations

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

**File:** core/sessions/localauth/orm.go (L43-59)
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
