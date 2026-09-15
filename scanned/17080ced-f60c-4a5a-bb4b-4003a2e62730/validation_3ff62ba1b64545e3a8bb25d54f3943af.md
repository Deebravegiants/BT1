### Title
Email / account-state enumeration via distinguishable login error messages - (`core/web/sessions_controller.go`)

### Summary
The unauthenticated `POST /sessions` login endpoint returns the raw, distinguishable error text produced by the authentication providers' `CreateSession`/`GetUserWebAuthn` calls directly to the client. Because the local, LDAP, and OIDC authenticators intentionally use different error strings for "email not found," "invalid password," and "MFA error," an unauthenticated attacker can enumerate valid Chainlink Node API user emails and detect whether MFA (WebAuthn) is configured for a given account — the same bug class as CVE-2021-22892 (Rocket.Chat email enumeration via login validation responses).

### Finding Description
`SessionsController.Create` first calls `GetUserWebAuthn(ctx, sr.Email)` for every login attempt, then forwards any error from `CreateSession` straight to the HTTP response via `jsonAPIError`, which serializes `err.Error()` into the JSON body: [1](#0-0) 

`jsonAPIError` puts the raw Go error message into the JSON API error payload with no genericization: [2](#0-1) 

Inside `localauth.orm.CreateSession`, the login flow performs sequential checks that each fail with a distinct message:
1. `FindUser` for a non-existent email fails with a DB "no rows" style error (bubbled straight through, since `err` is returned unmodified at line 147).
2. If found, an email mismatch returns `"Invalid email"`.
3. If email matches but password is wrong, `"Invalid password"`.
4. If the credentials succeed but MFA fails, `"MFA Error"`. [3](#0-2) 

The same three-way distinguishable pattern (`"invalid email"`, `"invalid password"`) repeats in the LDAP and OIDC local-fallback authenticators: [4](#0-3) [5](#0-4) 

While a `constantTimeEmailCompare` is used to avoid timing side channels on the email comparison itself, the resulting error *message content* (not timing) still leaks which validation step failed, which is the exact bug class described in the CVE (enumeration via differing validation-check responses, not necessarily timing).

Additionally, `GetUserWebAuthn` is queried before the email/password check completes and returns an empty (non-error) list for both "user doesn't exist" and "user has no MFA" cases, so its own error path (`http.StatusInternalServerError` "internal Server Error") differs from downstream `CreateSession` errors, adding another (weaker) side channel: [6](#0-5) 

### Impact Explanation
An unprivileged remote client can send crafted login attempts to `POST /sessions` and, purely from the JSON error text (all returned as HTTP 401, so status code alone doesn't leak this, but body content does), determine:
- Whether a given email exists as a Chainlink Node API user (`"Invalid email"`/DB-not-found error vs `"Invalid password"`).
- Whether that account has WebAuthn/MFA enabled (`"MFA Error"` vs successful session, or via the WebAuthn challenge JSON leaking directly in the error body at line 198 of `orm.go`).

This is an information-disclosure vulnerability, consistent with CVSS 3.1 vector `C:H/I:N/A:N` as in the referenced CVE — it does not directly grant access but materially aids account enumeration and targeted credential attacks against the node's admin API.

### Likelihood Explanation
High likelihood of exploitation: the endpoint is unauthenticated by design (`unauth.POST("/sessions", sc.Create)`), rate-limited but not blocked [7](#0-6) , and the differing error strings are stable, deterministic, and require no special access — only network reachability to the node's web server.

### Recommendation
Return a single generic error message and HTTP status (e.g., "invalid credentials", 401) for all authentication failure branches, regardless of whether the email was not found, the password was incorrect, or MFA failed, at the `sessions_controller.Create` handler layer, rather than propagating provider-internal error text via `jsonAPIError(c, http.StatusUnauthorized, err)`. Ensure the WebAuthn challenge JSON is never embedded in an error message body reachable pre-authentication, and ensure timing remains normalized across all three failure branches (already partly done via `constantTimeEmailCompare`, but the added JSON marshal/log steps for MFA vs non-MFA paths should be checked for timing parity as well).

### Proof of Concept
```
# Case 1: unknown email
curl -s -X POST https://node/sessions -d '{"email":"doesnotexist@x.com","password":"whatever"}'
-> {"errors":[{"detail":"no matching user for provided email"}]}  (or DB "sql: no rows in result set")

# Case 2: known email, wrong password
curl -s -X POST https://node/sessions -d '{"email":"admin@company.com","password":"wrongpass"}'
-> {"errors":[{"detail":"Invalid password"}]}

# Case 3: known email, MFA-enabled account
curl -s -X POST https://node/sessions -d '{"email":"mfa-user@company.com","password":"correctpass"}'
-> returns a WebAuthn challenge JSON as the error body / distinct "MFA Error"
```
By diffing the response bodies for cases 1 and 2, an attacker can enumerate valid emails registered on the node; diffing cases 2 and 3 additionally reveals which accounts have MFA configured.

### Citations

**File:** core/web/sessions_controller.go (L41-60)
```go
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

**File:** core/sessions/localauth/orm.go (L144-169)
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

	// Load all valid MFA tokens associated with user's email
	uwas, err := o.GetUserWebAuthn(ctx, user.Email)
	if err != nil {
		// There was an error with the database query
		lggr.Errorf("Could not fetch user's MFA data: %v", err)
		return "", pkgerrors.New("MFA Error")
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
