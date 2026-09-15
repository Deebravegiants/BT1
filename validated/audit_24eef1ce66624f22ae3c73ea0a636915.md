Confirmed: `jsonAPIError` returns `err.Error()` raw to the client in the JSON:API error body via `models.NewJSONAPIErrorsWith(err.Error())` [1](#0-0) .

### Title
Username enumeration via distinct login error messages on `/sessions` (`SessionsController.Create`) - (File: core/web/sessions_controller.go, core/sessions/localauth/orm.go)

### Summary
The `/sessions` login endpoint returns different, raw error text to unauthenticated callers depending on whether the submitted email corresponds to an existing user, allowing an attacker to enumerate valid usernames/emails — the same bug class as CVE-2026-21484 (differing responses based on account existence), just surfaced on the login flow rather than a distinct forgot-password endpoint (Chainlink has no such endpoint).

### Finding Description
`SessionsController.Create` accepts a `SessionRequest{Email, Password}` from an unauthenticated caller and forwards it to `AuthenticationProvider().CreateSession` [2](#0-1) . On error it calls `jsonAPIError(c, http.StatusUnauthorized, err)`, which serializes `err.Error()` directly into the JSON response body [3](#0-2) [1](#0-0) .

In the local-auth implementation, `orm.CreateSession` first calls `o.FindUser(ctx, sr.Email)`; if the email doesn't exist in the `users` table, the raw SQL-driver "not found" error propagates back unmodified. If the email *does* exist but the password is wrong, a distinct, human-readable `"Invalid password"` error is returned instead [4](#0-3) . These two code paths produce observably different error text/content for a nonexistent-account request vs. a valid-account/wrong-password request, both reachable from the same unauthenticated `/sessions` request.

The LDAP and OIDC providers exhibit the analogous pattern in their `localLoginFallback` methods, returning `"invalid email"` when the found user's email doesn't case-insensitively match, versus `"invalid password"` when the password check fails [5](#0-4) [6](#0-5) .

### Impact Explanation
An unprivileged, unauthenticated network client can distinguish "email exists" from "email does not exist" by inspecting the login error text/shape returned by `/sessions`, enabling systematic enumeration of valid admin/API user emails. This is low-severity information disclosure (matches the CVSS 5.3 / C:L profile of the reference CVE) — it does not itself grant authentication bypass or credential disclosure, but it materially aids targeted credential-stuffing or brute-force/social-engineering attacks against the node's admin UI.

### Likelihood Explanation
Likelihood is high: the `/sessions` endpoint requires no authentication, no rate limiting is evident in the reviewed code path, and the differing error content is a direct, deterministic function of account existence.

### Recommendation
Return a single generic, constant error message and status code for all `CreateSession`/login failures (unknown email, wrong password, and inactive/no-groups cases) across `localauth`, `ldapauth`, and `oidcauth` providers, and avoid leaking `err.Error()` verbatim through `jsonAPIError` for authentication failures — audit-log the specific failure reason (as is already done via `auditLogger.Audit(...)`) instead of returning it to the caller.

### Proof of Concept
1. `POST /sessions` with `{"email":"knownadmin@node.com","password":"wrongpassword"}` → response body contains `"Invalid password"`.
2. `POST /sessions` with `{"email":"doesnotexist@node.com","password":"wrongpassword"}` → response body contains a different message (DB "no rows"/generic not-found error rather than `"Invalid password"`), confirmed by the differing branches in `orm.CreateSession` [4](#0-3)  and the existing test `TestSessionsController_Create`, which already exercises "incorrect pwd" vs "incorrect email" as separate negative cases [7](#0-6) .
3. Comparing the two responses reveals which email is registered.

### Citations

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

**File:** core/web/sessions_controller_test.go (L33-42)
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
