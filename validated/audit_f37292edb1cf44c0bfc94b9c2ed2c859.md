Confirmed: the code exactly matches the claim. `jsonAPIError` (core/web/helpers.go:21-29) calls `err.Error()` and embeds it into the JSON response body via `models.NewJSONAPIErrorsWith(err.Error())` when the error is not already a `*models.JSONAPIErrors`, and `sessions_controller.go` (line 58) passes the raw `CreateSession` error directly to `jsonAPIError` without wrapping or sanitizing it. In `localauth/orm.go`, a nonexistent email causes `FindUser` (which wraps a raw SQL query via `o.ds.GetContext`) to return the unmodified underlying database error (typically containing `sql: no rows in result set`), while an existing email with a wrong password returns the fixed string `"Invalid password"` — these two error bodies are distinguishable by content even though both return HTTP 401. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

This is a genuine, unauthenticated, remotely-triggerable user-enumeration bug reachable via a single `POST /sessions` request with no prerequisites other than default local-auth configuration — the rate limiter only slows, not prevents, the attack.

Audit Report

## Title
Local-auth `/sessions` login endpoint reveals account existence via differing error messages - (File: core/sessions/localauth/orm.go)

## Summary
The unauthenticated `POST /sessions` endpoint (`core/web/router.go` L207-217) returns the raw, unsanitized error from `CreateSession` directly to the client via `jsonAPIError` in `core/web/sessions_controller.go` (L56-60). In `core/sessions/localauth/orm.go`, a non-existent email causes `FindUser`'s raw SQL/ORM error to propagate unmodified (L144-148), while an existing email with a wrong password returns the fixed string `"Invalid password"` (L159-162), making the two cases distinguishable to an unauthenticated caller.

## Finding Description
`sessionRoutes` registers `POST /sessions` behind only a rate limiter, with no authentication middleware, calling `SessionsController.Create`. Inside `Create`, any error from `AuthenticationProvider().CreateSession` is passed straight to `jsonAPIError(c, http.StatusUnauthorized, err)`. `jsonAPIError` (`core/web/helpers.go` L21-29) checks whether the error is already a `*models.JSONAPIErrors`; if not, it calls `models.NewJSONAPIErrorsWith(err.Error())`, embedding the raw Go error text into the JSON response body.

In `localauth.orm.CreateSession`, the very first step is `o.FindUser(ctx, sr.Email)`, which executes `SELECT * FROM users WHERE lower(email) = lower($1)` and returns the raw underlying error (e.g., `sql.ErrNoRows`-derived text) unmodified when the email does not exist. If the email does exist, subsequent checks return hand-crafted, generic strings `"Invalid email"` or `"Invalid password"`. Because these two paths produce differently-worded response bodies while sharing the same HTTP 401 status, an attacker who submits guesses can distinguish "email not found" (raw DB error text) from "email found, wrong password" (`"Invalid password"`), without needing any credential, role, or host access — exactly the response-differentiation pattern behind CVE-2022-44381.

## Impact Explanation
This allows unauthenticated enumeration of valid node operator/admin email addresses on the local-auth login endpoint, aiding targeted credential-stuffing, brute-force, and phishing campaigns against the node's admin API. This maps to a legitimate, if lower-severity, information-disclosure impact class (CWE-203, user enumeration) adjacent to node API authentication.

## Likelihood Explanation
The attack requires only a single unauthenticated HTTP POST per candidate email and no special privileges; the endpoint is rate-limited (`rl.UnauthenticatedPeriod()`/`rl.Unauthenticated()`), which slows but does not prevent enumeration over time. It applies to default local-auth deployments (non-LDAP/OIDC).

## Recommendation
Normalize all failure paths of `CreateSession` in `core/sessions/localauth/orm.go` to return a single generic error (e.g., `"invalid email or password"`) regardless of whether the email exists, and have `SessionsController.Create` avoid forwarding raw underlying error text to unauthenticated clients (e.g., wrap/replace it with a fixed generic message before calling `jsonAPIError`).

## Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@test.com","password":"anything"}` → HTTP 401 with body containing the raw `FindUser`/SQL error text (e.g., derived from `sql.ErrNoRows`).
2. `POST /sessions` with `{"email":"<valid-existing-email>","password":"wrongpassword"}` → HTTP 401 with body containing the literal string `"Invalid password"`.
3. A Go integration test hitting the `/sessions` route with a test DB containing one known user, comparing response bodies (not just status codes) for the two cases above, demonstrates the distinguishable content.

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
