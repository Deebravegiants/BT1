This confirms `jsonAPIError` places `err.Error()` verbatim into the JSON:API `detail` field via `models.NewJSONAPIErrorsWith(err.Error())`, and `SessionsController.Create` calls this directly with the error returned from `CreateSession`. The code in `core/sessions/localauth/orm.go` does confirm distinct error strings `"Invalid email"` and `"Invalid password"` (and a raw `sql.ErrNoRows`-style error when `FindUser` fails for a nonexistent email), exactly as claimed.

Audit Report

## Title
Unauthenticated `/sessions` login endpoint distinguishes "Invalid email" vs "Invalid password" errors, enabling user email enumeration - (File: core/sessions/localauth/orm.go)

## Summary
The `POST /sessions` endpoint forwards raw authentication errors from `CreateSession` straight to the client via `jsonAPIError`, and `CreateSession` in `core/sessions/localauth/orm.go` returns textually distinct errors ("Invalid email" vs "Invalid password", plus a bare `sql.ErrNoRows` for a fully unknown email) depending on which check fails. This lets an unauthenticated client distinguish "email not registered" from "email registered but wrong password," enabling enumeration of valid API user accounts on the node.

## Finding Description
`sessionRoutes` registers `POST /sessions` on the unauthenticated route group, gated only by a rate limiter: [1](#0-0) 

`SessionsController.Create` binds the request, calls `AuthenticationProvider().CreateSession`, and on error forwards it unmodified to `jsonAPIError`: [2](#0-1) 

`jsonAPIError` places `err.Error()` verbatim into the JSON:API error `detail` field returned to the caller: [3](#0-2) 

`CreateSession` in `core/sessions/localauth/orm.go` first calls `FindUser` (which can return `sql.ErrNoRows` for a nonexistent email), then checks email match and returns `"Invalid email"`, and only afterward checks the password hash and returns `"Invalid password"`: [4](#0-3) 

These three distinct failure modes (DB "no rows", "Invalid email", "Invalid password") are textually different and are returned unmodified to the unauthenticated client. No normalization or generic "invalid credentials" response exists in this path, and the only mitigating control is the configurable rate limiter, which slows but does not prevent probing.

## Impact Explanation
This is a legitimate account/email enumeration vulnerability: an unauthenticated attacker can determine whether an arbitrary email address corresponds to a registered Chainlink node API user by observing the distinct error text. This is a real, low-to-moderate severity information disclosure that could assist targeted credential-stuffing/brute-force campaigns against known-valid accounts on a node's admin API. It does not by itself grant authentication bypass, privilege escalation, fund movement, or key exfiltration — it is reconnaissance-only, and the actual account compromise still requires a correct password (or a separate vulnerability).

## Likelihood Explanation
The endpoint is unauthenticated and internet-facing by design, and the only control is `UnauthenticatedPeriod`/`Unauthenticated` rate limiting, which does not prevent enumeration outright, only slows it. Given a candidate email list, an external actor can trivially script this. This part of the report's likelihood argument holds up in the code as written.

## Recommendation
Normalize authentication failure responses in `CreateSession` (`core/sessions/localauth/orm.go`) and the LDAP/OIDC equivalents to return an identical generic error message/status regardless of whether the email exists or the password is wrong, and ensure `SessionsController.Create` (`core/web/sessions_controller.go`) never forwards the underlying error string verbatim to the client (e.g., translate internal errors to a fixed `"invalid credentials"` message at the controller boundary, independent of the underlying cause).

## Proof of Concept
1. `POST /sessions` with `{"email":"knownuser@example.com","password":"wrong"}` → response body `detail` contains `"Invalid password"`.
2. `POST /sessions` with `{"email":"doesnotexist@example.com","password":"wrong"}` → response body `detail` contains `"Invalid email"` or a distinct DB-lookup error.
3. Compare response bodies across a list of candidate emails to determine which are registered node users — confirmed reachable via the unauthenticated `/sessions` route (`core/web/router.go` L207-215) and the direct error-forwarding logic in `core/web/sessions_controller.go` L56-60 and `core/web/helpers.go` L21-29.

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
