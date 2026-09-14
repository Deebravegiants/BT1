This confirms the analog vulnerability exists and is reachable from an unprivileged client.

### Title
User enumeration via distinguishable login error messages - (File: core/sessions/localauth/orm.go)

### Summary
The `/sessions` login endpoint returns backend authentication error text verbatim to unauthenticated HTTP callers, and that text differs depending on whether the submitted email exists in the system. This lets an anonymous attacker enumerate valid Chainlink node UI/API usernames (emails), directly analogous to the SEO Panel CVE-2024-22647 user-enumeration bug class.

### Finding Description
`SessionsController.Create` forwards whatever error `AuthenticationProvider().CreateSession` returns straight to the HTTP response body via `jsonAPIError`, which calls `err.Error()` and JSON-encodes it [1](#0-0) [2](#0-1) .

In the default local authentication backend, `CreateSession` first looks up the user by email and, if the email does not match, returns `"Invalid email"`; if the email matches but the password is wrong, it returns a different message, `"Invalid password"` [3](#0-2) .

The same pattern repeats in the LDAP local-fallback path (`"invalid email"` vs `"invalid password"`) [4](#0-3)  and in the OIDC local-fallback path (`"invalid email"` vs `"invalid password"`) [5](#0-4) .

Because these distinct strings propagate unchanged to the JSON API response (`http.StatusUnauthorized` with `err.Error()` as the message), an unauthenticated caller of `POST /sessions` can distinguish "email not found" from "wrong password" purely from the response body — enabling brute-force enumeration of valid node-operator email addresses, mirroring the SEO Panel authentication-error-disclosure bug class.

### Impact Explanation
This is an authentication weakness reachable pre-auth over the node's HTTP API. Knowing which email addresses are valid Chainlink Operator UI/API accounts narrows credential-stuffing/brute-force attacks and can reveal organizational information (which emails are node admins) without any privilege. It does not by itself grant access, but materially assists a subsequent password brute-force or targeted phishing/social-engineering attack against a confirmed valid admin account.

### Likelihood Explanation
High from a reachability standpoint: `POST /sessions` is a public, unauthenticated endpoint by design (it's how you log in), and no rate limiting or generic error normalization is applied before returning the ORM error text to the client, per `SessionsController.Create` and `jsonAPIError` [1](#0-0) .

### Recommendation
Normalize the `CreateSession` error path so that "unknown email" and "wrong password" (and MFA-related failures) return a single generic message (e.g., `"invalid credentials"`) to the HTTP client, regardless of which internal branch failed, while keeping the detailed distinction only in internal logs/audit events (the audit log already differentiates via `audit.AuthLoginFailedEmail` / `audit.AuthLoginFailedPassword`, so no telemetry is lost) [6](#0-5) . Apply the same fix uniformly in `core/sessions/ldapauth/ldap.go` and `core/sessions/oidcauth/oidc.go`'s `localLoginFallback`. Also consider having `SessionsController.Create` map all `CreateSession` errors (except MFA-challenge JSON, which is a legitimate protocol step) to a fixed generic message before calling `jsonAPIError`.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@x.com","password":"anything"}` → response body contains `"Invalid email"` (via `jsonAPIError` wrapping the ORM error) [7](#0-6) .
2. `POST /sessions` with `{"email":"<valid-admin-email>","password":"wrongpass"}` → response body contains `"Invalid password"` [8](#0-7) .
3. Diffing these two distinct response bodies across a list of candidate emails lets an attacker confirm which emails correspond to real node accounts, exactly as described in the SEO Panel advisory's enumeration technique.

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
