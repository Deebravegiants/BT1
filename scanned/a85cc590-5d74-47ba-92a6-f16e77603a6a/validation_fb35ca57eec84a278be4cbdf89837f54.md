Confirmed: `jsonAPIError` serializes `err.Error()` directly into the JSON response body, so the login endpoint's error message reaches the unauthenticated caller verbatim. [1](#0-0) 

### Title
Unauthenticated Login Endpoint Leaks Account-Existence via Distinguishable Error Messages - (File: core/web/sessions_controller.go)

### Summary
The `/sessions` login endpoint (`SessionsController.Create`) returns the raw error from `AuthenticationProvider().CreateSession` directly to the unauthenticated caller. Because the local-auth ORM's `CreateSession` produces distinct, identifiable errors depending on whether an email exists in the `users` table, an unauthenticated attacker can enumerate valid user emails by observing the response body.

### Finding Description
`SessionsController.Create` calls `sc.App.AuthenticationProvider().CreateSession(ctx, sr)` and, on failure, forwards the returned error verbatim to the client via `jsonAPIError(c, http.StatusUnauthorized, err)`. [2](#0-1) 

`jsonAPIError` puts `err.Error()` into the JSON body that is sent back to the requester. [1](#0-0) 

In the local-auth implementation, `CreateSession` first looks up the user by email with `FindUser`, and if the email does not exist in the `users` table, the underlying SQL "no rows" error (e.g. `sql: no rows in result set`, possibly wrapped) is returned directly, without ever reaching the "Invalid email"/"Invalid password" checks: [3](#0-2) 

If the email *does* exist but the case-normalized comparison or password check fails, the code returns the distinct strings `"Invalid email"` or `"Invalid password"`: [4](#0-3) 

This produces three observably different error classes reaching the unauthenticated caller:
1. Unknown email → raw DB "no rows" style error.
2. Known email, mismatched password → `"Invalid password"`.
3. Known email edge case → `"Invalid email"`.

This is directly analogous to CVE-2016-4992's root cause: an unprivileged/unauthenticated actor can infer the existence of a named directory object (there, RDN component objects; here, user account/email rows) purely from divergent server responses to unauthenticated requests, without any credentials or exploitation of the LDAP/OIDC network-layer subsystems.

The OIDC and LDAP authenticators use the same pattern (`localLoginFallback` in both cases produces `"invalid email"` vs `"invalid password"` distinctly), so the same enumeration surface exists across all local-fallback logins. [5](#0-4) [6](#0-5) 

### Impact Explanation
An unauthenticated network attacker can send POST requests to `/sessions` with candidate email addresses and, purely from the HTTP response body, determine whether a given account exists on the node. This is a low-severity information-disclosure (account/user enumeration) that facilitates follow-on targeted credential-stuffing, phishing, or brute-force attacks against confirmed admin/edit accounts on Chainlink node operator dashboards. It does not by itself allow authentication bypass, secret disclosure, or fund movement — matching CVE-2016-4992's own "infer existence" (no confidentiality/integrity/availability impact beyond existence disclosure) severity profile.

### Likelihood Explanation
High likelihood of exploitation: the `/sessions` endpoint is unauthenticated by design (it's the login endpoint) and internet-facing on any exposed Chainlink Operator UI, requiring no privileges, tokens, or special network position — only a distinguishing HTTP response comparison.

### Recommendation
Normalize all login failure paths in `core/sessions/localauth/orm.go` (`CreateSession`), `core/sessions/oidcauth/oidc.go` (`localLoginFallback`), and `core/sessions/ldapauth/ldap.go` (`localLoginFallback`) to return a single generic, timing-safe error (e.g. `sessions.ErrorAuthFailed`) for all failure modes — unknown email, wrong password, and DB lookup errors — before the error is returned to `SessionsController.Create`. Ensure `jsonAPIError` in `core/web/sessions_controller.go` is only ever given this generic error, never the raw `FindUser`/SQL error, so the client-visible message and status code are identical regardless of whether the email exists.

### Proof of Concept
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"nonexistent@example.com","password":"whatever"}
```
Response body contains a raw SQL/lookup error string distinct from:
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"knownadmin@example.com","password":"wrongpassword"}
```
which returns `"Invalid password"` — allowing an attacker to distinguish valid from invalid emails by diffing the two response bodies. [7](#0-6) [2](#0-1)

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

**File:** core/web/sessions_controller.go (L56-60)
```go
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
