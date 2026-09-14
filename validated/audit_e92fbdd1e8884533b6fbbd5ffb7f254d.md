### Title
Unauthenticated `/sessions` login endpoint distinguishes "Invalid email" vs "Invalid password" errors, enabling user email enumeration - (File: core/sessions/localauth/orm.go)

### Summary
The `POST /sessions` login endpoint returns different, verbatim error text depending on whether the submitted email exists in the `users` table or the password is simply wrong. An unauthenticated attacker can submit arbitrary email/password combinations and use the distinct error strings to enumerate valid API user email addresses on the node, analogous to the SEO Panel password-reset email-enumeration bug (BIT-seopanel-2024-22646 / CVE-2024-22646), where differing responses to reset requests revealed whether an email was registered.

### Finding Description
`SessionsController.Create` is registered on the unauthenticated route group and accepts a raw `email`/`password` JSON body: [1](#0-0) 

It forwards credentials straight to `AuthenticationProvider().CreateSession`, and on any error returned by that call, serializes the error directly back to the caller via `jsonAPIError`: [2](#0-1) 

In the local-auth implementation, `CreateSession` first checks the found user's email against the submitted email and returns `"Invalid email"`; only if that succeeds does it check the password hash and return `"Invalid password"`: [3](#0-2) 

Because `FindUser`/`findUser` does a case-insensitive SQL lookup that returns `sql.ErrNoRows` for a nonexistent email (surfaced from `CreateSession`'s initial `FindUser` call) versus a distinct `"Invalid email"` string when the email doesn't case-normalize-match an existing record, and a separate `"Invalid password"` string when the email is valid but the password hash check fails, the two failure modes produce textually different error bodies: [4](#0-3) 

These distinct error strings (`"Invalid email"` vs `"Invalid password"`, plus a DB "no rows" style error for a completely unknown address) are passed unmodified into `jsonAPIError`, and other controllers in this codebase (e.g. `UserController.UpdatePassword`) confirm that `err.Error()` text is placed directly into the JSON:API `detail` field returned to the client: [5](#0-4) [6](#0-5) 

The `TestSessionsController_Create` test itself distinguishes "incorrect pwd" vs "incorrect email" as separate test cases with only a generic status-code assertion, but does not assert the response body text, so the enumeration channel is untested/unguarded: [7](#0-6) 

The endpoint is only protected by a rate limiter, not by response normalization: [8](#0-7) 

### Impact Explanation
An unauthenticated actor hitting `/sessions` can determine whether a given email address corresponds to a registered Chainlink node API user (admin/edit/run/view) by observing whether the response says "Invalid email" (account doesn't exist / mismatch) or "Invalid password" (account exists, wrong password). This directly maps to "cross-user response confusion" / unauthenticated information disclosure about account existence, which can be leveraged to build a target list for credential-stuffing or brute-force attacks against known-valid accounts, increasing the effectiveness of subsequent authentication-bypass attempts against the node's admin API.

### Likelihood Explanation
Likelihood is moderate: the endpoint is unauthenticated and internet-facing by design (`/sessions` is the standard login route, only gated by a configurable rate limiter), so any external actor can probe it. The only mitigating control is the `UnauthenticatedPeriod`/`Unauthenticated` rate limit, which slows but does not prevent enumeration over time or across many IPs.

### Recommendation
Normalize authentication failure responses so that invalid email and invalid password (and MFA-related failures) all return an identical, generic error message and status code (e.g., "invalid credentials") from `CreateSession` in `core/sessions/localauth/orm.go`, `ldapauth/ldap.go`, and `oidcauth/oidc.go`, and ensure `SessionsController.Create` in `core/web/sessions_controller.go` never forwards the underlying error string verbatim to the client. Consider using constant-time/generic error paths similar to the `constantTimeEmailCompare` pattern already used elsewhere in the OIDC login flow.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"knownuser@example.com","password":"wrong"}` → observe response body containing `"Invalid password"`.
2. Send `POST /sessions` with `{"email":"doesnotexist@example.com","password":"wrong"}` → observe response body containing `"Invalid email"` (or a distinct DB-lookup failure message).
3. Repeat step 1/2 for a list of candidate emails; the differing error text reveals which addresses are valid registered node users, exactly mirroring the email-enumeration pattern described in CVE-2024-22646.

### Citations

**File:** core/web/router.go (L207-215)
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
```

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
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

**File:** core/web/user_controller.go (L225-229)
```go
	if !utils.CheckPasswordHash(request.OldPassword, string(user.HashedPassword)) {
		u.App.GetAuditLogger().Audit(audit.PasswordResetAttemptFailedMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusConflict, errors.New("old password does not match"))
		return
	}
```

**File:** core/web/user_controller_test.go (L43-48)
```go
			name:           "Incorrect old password",
			reqBody:        `{"oldPassword": "wrong password"}`,
			wantStatusCode: http.StatusConflict,
			wantErrCount:   1,
			wantErrMessage: "old password does not match",
		},
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
