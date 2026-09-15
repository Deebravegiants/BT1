Audit Report

## Title
User enumeration via distinguishable login error messages on `/sessions` endpoint - (File: `core/sessions/localauth/orm.go`)

## Summary
The unauthenticated `POST /sessions` endpoint returns different, verbatim error text depending on whether an email exists in the `users` table. When the email is unknown, `CreateSession` propagates the raw database error (e.g. `sql: no rows in result set`) from `findUser`; when the email exists but the password is wrong, it returns a distinct hardcoded `"Invalid password"` error. Both are serialized directly into the JSON API response body, letting an unauthenticated caller enumerate valid node user emails.

## Finding Description
`SessionsController.Create` calls `AuthenticationProvider().CreateSession(ctx, sr)` and on any error passes it straight to `jsonAPIError`, which serializes `err.Error()` into the client-visible JSON body: [1](#0-0) [2](#0-1) 

`CreateSession` first calls `o.FindUser(ctx, sr.Email)`, which delegates to `findUser`, executing `SELECT * FROM users WHERE lower(email) = lower($1)` via `o.ds.GetContext`. If no row matches, the raw driver error (`sql.ErrNoRows`, surfaced as `"sql: no rows in result set"`) is returned unwrapped: [3](#0-2) [4](#0-3) 

If the email is found but the password check fails, a distinct, hardcoded error is returned instead: [5](#0-4) 

The `/sessions` route requires no authentication, only rate limiting: [6](#0-5) 

This confirms the two code paths produce genuinely different response bodies (`"sql: no rows in result set"` vs `"Invalid password"`) for an unauthenticated POST request, and no normalization or generic-error wrapping exists between `FindUser`'s raw error and the client response. The existing test suite (`core/web/sessions_controller_test.go`) only checks status codes (`>= 400`) for negative cases, not response body content, so this discrepancy is untested.

## Impact Explanation
This is an information-disclosure issue (CWE-203, user enumeration), the same class as CVE-2023-38871. It allows an unauthenticated network client to determine whether a specific email address corresponds to a registered Chainlink node admin/API user by observing distinct error text in the response body. On its own this does not grant authentication bypass or fund movement, but it materially aids targeted credential-stuffing/brute-force attacks against node operator accounts, which is a legitimate low-severity finding under information-disclosure impact categories.

## Likelihood Explanation
The endpoint is reachable by any unprivileged client that can send an HTTP POST to the node's web server, with no authentication required (only rate limiting via `rateLimiter`). Exploitation requires a single request per probed email, making it trivially repeatable up to the configured rate limit.

## Recommendation
Normalize the error returned for both "email not found" and "wrong password" cases to a single generic message (e.g., `"invalid email or password"`) in `CreateSession` (`core/sessions/localauth/orm.go`), and apply the same normalization in the OIDC (`core/sessions/oidcauth/oidc.go`) and LDAP (`core/sessions/ldapauth/ldap.go`) local-fallback paths. Ensure `jsonAPIError` does not leak raw driver/DB error text (like `sql.ErrNoRows`) to unauthenticated clients on this route. Consider constant-time delay to reduce timing-based enumeration as a secondary mitigation.

## Proof of Concept
```
# Case 1: unknown email
curl -i -X POST https://node/sessions \
  -H 'Content-Type: application/json' \
  -d '{"email":"doesnotexist@example.com","password":"whatever"}'
# -> body contains raw DB error, e.g. "sql: no rows in result set"

# Case 2: known email, wrong password
curl -i -X POST https://node/sessions \
  -H 'Content-Type: application/json' \
  -d '{"email":"knownadmin@example.com","password":"wrongpassword"}'
# -> body contains "Invalid password"
```
A Go integration test extending `core/web/sessions_controller_test.go` to assert on `resp.Body` content (instead of only status code) for the `"incorrect pwd"` and `"incorrect email"` test cases would concretely demonstrate the differing, distinguishable error text.

### Citations

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

**File:** core/sessions/localauth/orm.go (L43-59)
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

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
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
