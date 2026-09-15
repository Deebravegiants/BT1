Audit Report

## Title
Username Enumeration via Distinct Login Error Messages - (File: `core/web/sessions_controller.go`)

## Summary
`SessionsController.Create` forwards the raw error from `AuthenticationProvider().CreateSession` directly into `jsonAPIError`, which serializes `err.Error()` into the JSON:API response body without normalization. The local authenticator (and equivalently the LDAP and OIDC local-admin fallback paths) produces the textually distinct errors `"Invalid email"` vs `"Invalid password"` depending on which check fails, and this distinction is confirmed to propagate unmodified to the unauthenticated caller.

## Finding Description
`SessionsController.Create` calls `CreateSession` and, on failure, passes the error straight to `jsonAPIError(c, http.StatusUnauthorized, err)`: [1](#0-0) 

`jsonAPIError` serializes the error message text directly into the response when the error is not a `*models.JSONAPIErrors`: [2](#0-1) 

In `localauth/orm.go`, `CreateSession` calls `FindUser` first; if that fails (e.g., no such user in DB), that error is returned as-is at line 147. If the user is found but the email comparison fails (a defense-in-depth check after a case-insensitive DB lookup), a distinct `"Invalid email"` error is returned; if the password check fails, `"Invalid password"` is returned: [3](#0-2) 

The email-mismatch branch at line 154-157 is a secondary defense check that runs after `FindUser` already succeeded via case-insensitive lookup — it is not the primary "user not found" path. The primary "user does not exist" path returns whatever error `FindUser` produces (not examined to completion in this review, but distinct from `"Invalid password"` in any case). Either way, the password-failure branch (`"Invalid password"`) is textually and observably distinct from any error returned for a nonexistent/mismatched email, and this distinction reaches the client verbatim through `jsonAPIError`. The identical pattern exists in the LDAP and OIDC local-admin fallback authenticators: [4](#0-3) [5](#0-4) 

The `/sessions` POST route sits in the unauthenticated route group, reachable by any unauthenticated client, only throttled (not blocked) by rate limiting: [6](#0-5) 

No sanitization or generic-error normalization exists between the authenticator layer and the HTTP response layer for this endpoint.

## Impact Explanation
An unauthenticated attacker submitting `POST /sessions` with varying email/password combinations receives a response whose error text differs based on whether the email/user lookup failed versus the password check failed. This allows enumeration of valid registered emails/usernames for the node's admin login (CWE-204, Observable Response Discrepancy), which is a legitimate stepping stone for targeted credential-stuffing or phishing against a node operator's admin account — an in-scope confidentiality impact on principal identifiers, though it does not itself grant authentication bypass, key exfiltration, or fund movement.

## Likelihood Explanation
The endpoint is unauthenticated and internet-facing in non-firewalled deployments; the divergent-error condition triggers under normal login flow with no special preconditions beyond submitting a login attempt, so it is trivially and repeatably reachable by any unprivileged actor. The `rl.Unauthenticated()` rate limiter on this route slows but does not prevent enumeration.

## Recommendation
Return a single generic error (e.g., `"invalid email or password"`) from `SessionsController.Create` for all `CreateSession` authentication failures, regardless of underlying cause (email lookup failure, email mismatch, or password mismatch), across the local, LDAP, and OIDC authenticators. Preserve the specific failure reason only in server-side audit logs (`AuthLoginFailedEmail` / `AuthLoginFailedPassword`), which are already recorded distinctly.

## Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@example.com","password":"anything"}` → observe the JSON:API error body text (sourced from `FindUser`'s error or `"Invalid email"` in `core/sessions/localauth/orm.go`).
2. `POST /sessions` with `{"email":"<a known/guessed valid email>","password":"wrongpassword"}` → observe the JSON:API error body contains `"Invalid password"` (`core/sessions/localauth/orm.go:161`).
3. Diff the two response bodies; the distinct text allows automated differentiation between "email not registered" and "email registered, wrong password" across a wordlist, confirming enumeration capability.

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

**File:** core/sessions/ldapauth/ldap.go (L631-639)
```go
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		l.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		l.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L586-594)
```go
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
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
