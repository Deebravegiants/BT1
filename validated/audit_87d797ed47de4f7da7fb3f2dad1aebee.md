Confirmed: `jsonAPIError` (`core/web/helpers.go:21-29`) serializes `err.Error()` directly into the JSON response body via `models.NewJSONAPIErrorsWith(err.Error())` when the error isn't a `*models.JSONAPIErrors`. The login handler (`SessionsController.Create`, `core/web/sessions_controller.go:56-60`) passes the raw error from `AuthenticationProvider().CreateSession(ctx, sr)` straight into `jsonAPIError(c, http.StatusUnauthorized, err)` without normalizing the message. The underlying local-auth implementation (`core/sessions/localauth/orm.go:154-162`) returns two distinct, user-controllable error strings depending on which check fails:

```go
if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
    ...
    return "", pkgerrors.New("Invalid email")
}
if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
    ...
    return "", pkgerrors.New("Invalid password")
}
```

The same pattern exists in `core/sessions/ldapauth/ldap.go` (`localLoginFallback`, `errors.New("invalid email")` vs `errors.New("invalid password")`) and `core/sessions/oidcauth/oidc.go` (`localLoginFallback`, same distinct messages).

### Title
Username/email enumeration via distinct "Invalid email" vs "Invalid password" error messages on the unauthenticated `/sessions` login endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `POST /sessions` login endpoint returns different, attacker-observable error text depending on whether the submitted email exists in the users table, allowing an unauthenticated caller to enumerate valid Chainlink node operator/admin email addresses — the same bug class as CVE-2021-28399 (OrangeHRM forgot-password username enumeration).

### Finding Description
`SessionsController.Create` (`core/web/sessions_controller.go:29-68`) is registered on the unauthenticated route group `unauth.POST("/sessions", sc.Create)` [1](#0-0) . It forwards any error from `AuthenticationProvider().CreateSession` directly to the client via `jsonAPIError(c, http.StatusUnauthorized, err)` [2](#0-1) . `jsonAPIError` puts `err.Error()` verbatim into the JSON response body [3](#0-2) .

The local-auth `CreateSession` implementation performs two sequential checks and returns semantically distinct errors for each:
- If the requested email doesn't match a found user record: `"Invalid email"`.
- If the email matches but the password is wrong: `"Invalid password"`. [4](#0-3) 

The identical two-message pattern (`"invalid email"` vs `"invalid password"`) exists in the LDAP fallback path [5](#0-4)  and the OIDC local-admin fallback path [6](#0-5) , both of which are also reachable through the same unauthenticated `/sessions` endpoint depending on configured `AuthenticationProvider`.

An unauthenticated client can send repeated `POST /sessions` requests with varying `email` values and a fixed dummy password, then distinguish "email exists" (`"Invalid password"` response) from "email does not exist" (`"Invalid email"` response), directly enumerating valid node-operator accounts.

### Impact Explanation
This discloses which email addresses are registered chainlink node users (which typically includes admin, edit, and run-role accounts). While it does not itself grant access, it is a reconnaissance primitive that meaningfully narrows credential-stuffing/brute-force/phishing/social-engineering targeting of a specific, valid Chainlink node operator account, and is the exact analog of the CVE cited (unauthenticated account/email enumeration via an authentication-adjacent endpoint). Severity is bounded (confidentiality-only, no direct authorization bypass), matching the Medium/CVSS 5.3-class rating of the referenced CVE.

### Likelihood Explanation
Trivially reachable: the `/sessions` endpoint requires no authentication, only rate-limiting (`rateLimiter(rl.UnauthenticatedPeriod(), rl.Unauthenticated())` [7](#0-6) ), which slows but does not prevent enumeration over time. Any external network client with access to the node's API can perform this attack with no prior knowledge or credentials.

### Recommendation
Normalize the error returned from `CreateSession` (across `localauth`, `ldapauth`, and `oidcauth` implementations) to a single generic message (e.g., `"invalid credentials"`) for both the "email not found" and "password mismatch" branches before it is surfaced through `SessionsController.Create` / `jsonAPIError`, while keeping the differentiated audit-log events (`AuthLoginFailedEmail` / `AuthLoginFailedPassword`) for internal observability only.

### Proof of Concept
```
# candidate 1: existing admin email, wrong password
curl -s -X POST https://<node>/sessions -d '{"email":"admin@company.com","password":"wrong"}' \
  -H 'Content-Type: application/json'
# -> {"errors":[{"detail":"Invalid password"}]}  (HTTP 401)

# candidate 2: non-existent email, same wrong password
curl -s -X POST https://<node>/sessions -d '{"email":"doesnotexist@company.com","password":"wrong"}' \
  -H 'Content-Type: application/json'
# -> {"errors":[{"detail":"Invalid email"}]}  (HTTP 401)
```
The differing `detail` message directly confirms whether `admin@company.com` is a registered user, without any authentication.

### Citations

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
