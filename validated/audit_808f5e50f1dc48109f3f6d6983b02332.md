Confirmed: `jsonAPIError` at [1](#0-0)  serializes `err.Error()` directly into the JSON response body sent to the client. This is the concrete mechanism that turns internal error-message differences into an externally observable oracle.

Based on this investigation, I found a real user-enumeration analog in the unauthenticated `/sessions` login endpoint.

### Title
User Enumeration via Distinguishable Error Messages on Unauthenticated Login Endpoint - (File: core/web/sessions_controller.go)

### Summary
The `POST /sessions` endpoint (`SessionsController.Create`) is reachable without authentication and returns different, verbatim error messages to the client depending on whether the submitted email corresponds to an existing user, an existing user with a wrong password, or a nonexistent user. This mirrors the CVE-2023-38327 bug class: an unauthenticated endpoint whose server response differs based on internal account-lookup state, allowing enumeration of valid usernames/emails.

### Finding Description
`SessionsController.Create` at [2](#0-1)  binds the request, then calls `AuthenticationProvider().CreateSession(ctx, sr)`. On failure it forwards the raw error straight to the client via `jsonAPIError(c, http.StatusUnauthorized, err)` at line 58.

For the default local-auth provider, `orm.CreateSession` at [3](#0-2)  first calls `o.FindUser(ctx, sr.Email)`, which runs a direct SQL lookup (`findUser`, [4](#0-3) ). If the email does not exist in the `users` table, this returns the raw `sql.ErrNoRows` error (message: `sql: no rows in result set`), which propagates unmodified back to `CreateSession`'s caller and then to the HTTP response.

If the email *does* exist but the password is wrong, a completely different error string, `"Invalid password"`, is returned (line 161). If the email casing/comparison fails, `"Invalid email"` is returned (line 156).

`jsonAPIError` at [1](#0-0)  puts `err.Error()` directly into the JSON body returned to the (unauthenticated) HTTP client, so these three distinct messages — SQL-lookup-miss text vs. `"Invalid password"` vs. `"Invalid email"` — are all directly observable by an anonymous caller of `/sessions`.

The same pattern (distinct error text depending on lookup result) is duplicated in the LDAP and OIDC local-fallback authenticators as well: [5](#0-4)  and [6](#0-5) .

### Impact Explanation
An unauthenticated attacker can send crafted email/password combinations to `/sessions` and use the differing error text (`sql: no rows in result set` vs `Invalid password`) to determine whether a given email address is a registered API user of the Chainlink node. This is classic account/user enumeration (CWE-203/CWE-204), which can then be leveraged for targeted credential-stuffing or brute-force attacks against confirmed valid accounts. Impact is limited to confidentiality of account existence — it does not directly grant authentication bypass or fund movement, so severity is moderate, matching the Medium/CVSS 5.3 rating of the reference CVE (`AC:L/PR:N/UI:N/C:L/I:N/A:N`).

### Likelihood Explanation
High likelihood of exploitability: the endpoint requires no authentication, no rate limiting is evident in this code path, and the distinguishing error text is returned synchronously on every request, making it trivial to script an enumeration sweep.

### Recommendation
Normalize the error message and HTTP status returned by `/sessions` for all authentication-failure cases (unknown email, wrong password, wrong email casing) to a single generic message such as `"invalid credentials"`, matching timing as closely as possible (constant-time comparison is already used for email/password matching, but the SQL "no rows" path should also be normalized before it reaches `jsonAPIError`). This should be applied uniformly across `localauth`, `ldapauth`, and `oidcauth` `CreateSession`/`localLoginFallback` implementations.

### Proof of Concept
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"nonexistent@example.com","password":"anything"}
```
Response body contains: `{"errors":[{"detail":"sql: no rows in result set"}]}`

```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"knownuser@example.com","password":"wrongpassword"}
```
Response body contains: `{"errors":[{"detail":"Invalid password"}]}`

The differing `detail` field content lets an anonymous client distinguish whether `knownuser@example.com` is a registered account.

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

**File:** core/sessions/localauth/orm.go (L55-59)
```go
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
