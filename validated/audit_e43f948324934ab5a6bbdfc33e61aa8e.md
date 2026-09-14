### Title
Account Enumeration via Login Response Differential in Local Session Authentication - (File: `core/sessions/localauth/orm.go`)

### Summary
The `CreateSession` login flow returns a raw database error for non-existent email addresses, but a distinct hand-crafted "Invalid password"/"Invalid email" error for existing accounts. Because this error text is echoed verbatim to the unauthenticated client, an attacker can distinguish "no such user" from "user exists, wrong credentials" and enumerate valid Chainlink node API user emails.

### Finding Description
`SessionsController.Create` binds the login payload and passes it straight to `AuthenticationProvider().CreateSession`, then reflects any error back to the client with the same HTTP status but the underlying error text: [1](#0-0) 

In the local auth provider, `CreateSession` first looks up the user by email. If the lookup fails (no such user), the raw ORM/database error (effectively "no rows in result set" from `GetContext`) is returned unmodified: [2](#0-1) 

If the user does exist but the password is wrong, a different, hand-authored error string is returned instead: [3](#0-2) 

Both errors are surfaced to the caller via `jsonAPIError`, which serializes `err.Error()` directly into the JSON response body without normalization: [4](#0-3) 

The same pattern repeats in the LDAP and OIDC local-fallback authenticators, which also emit "invalid email" vs "invalid password" distinctly, though those still don't leak the *user-not-found* case as a raw DB error text: [5](#0-4) [6](#0-5) 

The `/sessions` login endpoint is reachable by unauthenticated clients (only IP-based rate limiting applies, no account/email-based lockout exists in Chainlink at all): [7](#0-6) 

This is structurally the same bug class as the Budibase report: an observable, message-level differential response to the login endpoint depending solely on whether the submitted email exists in the backing store — CWE-204 Observable Response Discrepancy.

### Impact Explanation
An unauthenticated attacker submitting a single POST to `/sessions` with an arbitrary email/password pair can determine whether that email corresponds to a real Chainlink node operator account, based on the differing error text ("no rows in result set"-style DB error vs. "Invalid password"). This enables:
- Enumeration of valid operator/admin emails on a given Chainlink node, useful for targeted credential-stuffing, phishing, or brute-force focusing.
- No rate limiting is scoped per-account, so this differential can be probed at the general unauthenticated rate limit (`rl.UnauthenticatedPeriod()`/`rl.Unauthenticated()`), not a stricter per-account throttle.

Impact is limited to information disclosure (email existence) — it does not by itself grant authentication bypass or credential disclosure, consistent with the Medium/CWE-204 classification of the source report.

### Likelihood Explanation
Trivial to exploit: a single unauthenticated HTTP request per email guess is enough to distinguish existing vs. non-existing accounts; no timing analysis or repeated attempts are required, unlike the original Budibase lockout-based variant.

### Recommendation
Normalize all login failure responses (user not found, wrong password, wrong email case, MFA errors) to an identical generic error message and status code before they reach `jsonAPIError`, e.g. wrap the "no such user" case in `orm.CreateSession` with the same `"Invalid email"`/`"Invalid password"`-shaped message rather than returning the raw `FindUser` error. Apply the same normalization in `ldapauth` and `oidcauth` local fallback paths for consistency.

### Proof of Concept
```bash
# Existing user, wrong password
curl -s -X POST http://localhost:6688/sessions \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"wrongpass"}'
# -> {"errors":[{"detail":"Invalid password"}]}

# Non-existing user
curl -s -X POST http://localhost:6688/sessions \
  -H 'Content-Type: application/json' \
  -d '{"email":"doesnotexist@example.com","password":"wrongpass"}'
# -> {"errors":[{"detail":"sql: no rows in result set"}]}  (raw DB error, different text)
```
The differing error text (`"Invalid password"` vs. a raw SQL "no rows" error) confirms account existence to an unauthenticated caller.

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
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

**File:** core/web/auth/helpers.go (L15-23)
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
