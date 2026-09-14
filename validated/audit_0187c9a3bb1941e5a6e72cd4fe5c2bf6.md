### Title
Account Enumeration via Differential Error Messages on Unauthenticated `/sessions` Login Endpoint - (File: `core/sessions/localauth/orm.go`)

### Summary
The unauthenticated `POST /sessions` login endpoint returns different, verbatim backend error strings depending on whether the submitted email corresponds to an existing account, allowing an unprivileged remote attacker to enumerate valid user email addresses. This is analogous to CVE-2016-4947 (Cloudera HUE), where an unauthenticated endpoint disclosed account existence, except here the oracle is differential error text on the login path rather than an autocomplete endpoint.

### Finding Description
`SessionsController.Create` is reachable without any authentication [1](#0-0) . It forwards the client-supplied email/password directly to `AuthenticationProvider().CreateSession` and returns any resulting error verbatim to the caller via `jsonAPIError`, which serializes `err.Error()` into the JSON response body [2](#0-1) [3](#0-2) .

In the local auth ORM implementation, `CreateSession` first calls `FindUser`, which performs `SELECT * FROM users WHERE lower(email) = lower($1)` via `sqlx`'s `GetContext` [4](#0-3) [5](#0-4) . When no matching row exists, `sqlx.GetContext` returns the raw `sql.ErrNoRows` (i.e., `"sql: no rows in result set"`), and `CreateSession` propagates that error unmodified:

```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err   // raw sql.ErrNoRows surfaces here for non-existent email
	}
	...
	if !constantTimeEmailCompare(...) {
		return "", pkgerrors.New("Invalid email")   // different message when case-mismatch is caught downstream
	}
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		return "", pkgerrors.New("Invalid password")  // different message for existing email, wrong password
	}
	...
}
``` [6](#0-5) 

This produces three observably distinct outcomes for an unauthenticated caller of `POST /sessions`:
1. Email does not exist in the `users` table → HTTP 401 body containing `"sql: no rows in result set"`.
2. Email exists but password is wrong → HTTP 401 body containing `"Invalid password"`.
3. Email exists, password correct → HTTP 200 with session cookie.

The existing `constantTimeEmailCompare` mitigation only equalizes timing/messages for the (unreachable in local-only path) case where `FindUser` succeeds but the returned row's email differs from the input by more than casing; it does nothing for the more common not-found case, where the raw SQL driver error leaks through. The same pattern repeats in the `ldapauth` and `oidcauth` "local admin fallback" code paths, which also call `FindUser`-equivalent lookups and can leak `sql.ErrNoRows` before the "Invalid email"/"Invalid password" checks are reached [7](#0-6) [8](#0-7) .

### Impact Explanation
An unauthenticated remote client can distinguish "no such account" from "wrong password" purely from the HTTP response body of `/sessions`, without any privileges. This enables systematic enumeration of valid node admin/operator email addresses, which is a direct precursor to credential-stuffing, targeted phishing, or brute-force password attacks against the node's admin UI/API — the same bug class and impact tier (CWE-200 information disclosure enabling account enumeration) as the referenced Cloudera HUE advisory. It does not by itself grant authentication bypass or fund movement, keeping severity at Medium, consistent with the CVSS of the analog advisory (AV:N/AC:L/PR:N/UI:N/C:L).

### Likelihood Explanation
High likelihood of exploitation: the endpoint is intentionally internet/network reachable pre-authentication (it's the login endpoint itself), requires no special access, and the differential response is deterministic and trivially observable by any client capable of sending a JSON POST request.

### Recommendation
Normalize all failure paths of `CreateSession` (and its LDAP/OIDC local-fallback equivalents) to return a single generic, constant error (e.g., `"invalid email or password"`) regardless of whether the email lookup failed, the email mismatched, or the password check failed, and ensure the error object returned to `SessionsController.Create` never leaks the underlying driver error text (avoid propagating `sql.ErrNoRows` or any other DB error directly to `jsonAPIError`). Additionally, apply constant-time behavior across the "user not found" and "wrong password" branches to avoid a timing side channel replacing the removed message side channel.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@example.com","password":"anything"}` → observe HTTP 401 body `{"errors":[{"detail":"sql: no rows in result set"}]}`.
2. `POST /sessions` with `{"email":"<known-existing-admin-email>","password":"wrongpassword"}` → observe HTTP 401 body `{"errors":[{"detail":"Invalid password"}]}`.
3. The differing `detail` fields between (1) and (2) allow an attacker to enumerate which emails correspond to real accounts on the node, without needing any prior authentication.

Note: I was unable to execute the endpoint live to confirm the exact wording of the JSON body in this environment; the analysis is based on static tracing of `SessionsController.Create` → `AuthenticationProvider.CreateSession` → `orm.FindUser`/`sqlx.GetContext` error propagation shown above. A Devin session with runtime access would be needed to confirm the literal HTTP response bytes.

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

**File:** core/sessions/localauth/orm.go (L44-46)
```go
func (o *orm) FindUser(ctx context.Context, email string) (sessions.User, error) {
	return o.findUser(ctx, email)
}
```

**File:** core/sessions/localauth/orm.go (L55-58)
```go
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

**File:** core/sessions/ldapauth/ldap.go (L622-641)
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
