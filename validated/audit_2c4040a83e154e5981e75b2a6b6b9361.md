Audit Report

## Title
Observable Discrepancy Enabling Email Enumeration via Login Error Messages - (File: core/sessions/localauth/orm.go)

## Summary
`CreateSession` in `core/sessions/localauth/orm.go` returns the raw ORM/SQL error when `FindUser` fails to locate a user by email, but returns distinct deliberately-worded strings ("Invalid email" / "Invalid password") when the user is found but authentication fails. These errors flow unmodified into the HTTP response via `jsonAPIError`, which calls `models.NewJSONAPIErrorsWith(err.Error())` and returns the literal error text to the client.

## Finding Description
`FindUser`/`findUser` executes `SELECT * FROM users WHERE lower(email) = lower($1)` and returns the raw `sqlutil.DataSource.GetContext` error (e.g., `sql.ErrNoRows` or its driver-specific text) directly to the caller when the email is not found: [1](#0-0)  This error is passed straight back out of `CreateSession` without normalization: [2](#0-1) 

Conversely, if the email is found but the case-insensitive comparison or password check fails, distinct hardcoded strings are returned: [3](#0-2) 

`SessionsController.Create` forwards this error unmodified to `jsonAPIError`: [4](#0-3)  and `jsonAPIError` serializes `err.Error()` verbatim into the JSON response body: [5](#0-4)  This confirms the raw, distinguishable text reaches the client, not just an internal log.

The `/sessions` POST route is registered in an unauthenticated group subject only to rate limiting, so any unprivileged/anonymous client can reach this code path: [6](#0-5)  No existing middleware normalizes or redacts the error text before it reaches the response.

The same pattern is separately replicated in the LDAP local-fallback and OIDC authenticators, which return `"invalid email"` vs `"invalid password"` vs a raw SQL lookup error, though those are used mainly for CLI/API-key-based flows.

## Impact Explanation
This is a genuine observable-discrepancy bug: an unauthenticated caller can distinguish "email not registered" (raw DB error text, e.g., containing `sql: no rows in result set`) from "email registered but wrong password" (`"Invalid password"`) or "case-mismatched email" (`"Invalid email"`). This enables systematic enumeration of registered node-admin/API email addresses, aiding targeted credential-stuffing or phishing campaigns. It does not directly expose credentials, keys, funds, or grant any unauthorized action — the impact is limited to information disclosure of account existence, matching a Medium/Low information-disclosure classification and the same bug class as the referenced NocoDB CVE.

## Likelihood Explanation
High feasibility: no authentication, role, or prior credential is required. An external client can POST arbitrary email/password pairs to `/sessions` and observe differing error text in the JSON response, limited only by the configured rate limiter (which does not prevent, only slows, enumeration).

## Recommendation
Normalize all failure paths in `CreateSession` (missing user, email mismatch, wrong password) to return an identical generic error (e.g., "invalid email or password") with identical structure before it reaches `jsonAPIError`. Apply the same normalization in `ldapauth.localLoginFallback` and `oidcauth` local fallback. Consider constant-time/constant-latency handling to also mitigate timing-based enumeration (e.g., always perform a dummy password hash comparison when the user is not found).

## Proof of Concept
1. `POST /sessions` with `{"email":"knownadmin@example.com","password":"wrongpass"}` → response body contains `"Invalid password"` (via `jsonAPIError` → `models.NewJSONAPIErrorsWith`).
2. `POST /sessions` with `{"email":"doesnotexist@example.com","password":"wrongpass"}` → response body contains the raw DB error text (e.g., `sql: no rows in result set`), which is structurally/textually different from case 1.
3. Comparing the two 401 response bodies reveals which email is registered, confirming enumeration is possible without authentication.

A minimal Go integration test against `SessionsController.Create` (using a test DB with one seeded user) POSTing both a known and unknown email and asserting the differing error strings in the JSON response would concretely demonstrate this.

### Citations

**File:** core/sessions/localauth/orm.go (L55-59)
```go
func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
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

**File:** core/web/sessions_controller.go (L56-60)
```go
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
