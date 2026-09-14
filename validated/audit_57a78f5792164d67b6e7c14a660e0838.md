Confirmed: `jsonAPIError` places the raw error text directly into the JSON response body via `models.NewJSONAPIErrorsWith(err.Error())`, as shown at [1](#0-0) , and `CreateSession` in the local auth ORM returns distinct literal error strings — `"Invalid email"` for a nonexistent user versus `"Invalid password"` for a valid user with wrong credentials — both surfaced with the same 401 status code, as shown at [2](#0-1) , and returned unmodified to the client in `SessionsController.Create` at [3](#0-2) .

### Title
Username Enumeration via Distinct Error Messages on `/sessions` Login Endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The `/sessions` login endpoint returns different, attacker-visible error message text depending on whether the submitted email corresponds to an existing user account, allowing unauthenticated enumeration of valid Chainlink node user accounts — directly analogous to the CVE-2020-25200 Pritunl username-enumeration bug class (distinguishable server responses for valid vs. invalid usernames during login).

### Finding Description
The unauthenticated `POST /sessions` route, registered in `sessionRoutes`, forwards login attempts to `SessionsController.Create`, [4](#0-3) . `Create` calls `AuthenticationProvider().CreateSession`, and on any error returns the error verbatim to the client with `jsonAPIError(c, http.StatusUnauthorized, err)` [3](#0-2) . `jsonAPIError` places `err.Error()` directly into the JSON response body's `detail` field with no redaction [1](#0-0) .

In the local-auth ORM's `CreateSession`, two distinct code paths produce two distinct literal error strings for the exact same HTTP status code (401):
- Email doesn't match any existing user record → `pkgerrors.New("Invalid email")`
- Email matches, but password is wrong → `pkgerrors.New("Invalid password")` [2](#0-1) 

Because both paths return the same 401 status code but different message text in the response body, an unauthenticated caller submitting arbitrary email guesses with an incorrect password can trivially distinguish "email does not exist" (`"Invalid email"`) from "email exists" (`"Invalid password"`) on the very first attempt — without needing the 20-attempt threshold behavior described in the CVE. The same pattern repeats in the OIDC and LDAP local-fallback authenticators (`"invalid email"` vs `"invalid password"`) [5](#0-4) .

The only mitigating control is a coarse IP-based rate limiter on unauthenticated session requests (5 requests / 20s by default), which slows but does not prevent enumeration [6](#0-5) .

### Impact Explanation
An attacker can enumerate valid Chainlink node administrator/operator email addresses without any credentials. This does not by itself grant access, but it materially aids follow-on credential-stuffing, password-spraying, or social-engineering attacks against a known-valid account list, and can leak information about which operators/organizations run a given node.

### Likelihood Explanation
High for a determined unauthenticated attacker: the endpoint is internet-facing by default, requires no prior authentication, and only a basic per-IP rate limiter (configurable, default 5 requests/20s) stands between the attacker and mass enumeration — easily bypassed with distributed source IPs.

### Recommendation
Normalize the error message and response detail for both "unknown email" and "wrong password" cases (e.g., always return a generic `"Invalid email or password"` message) so the response body content does not leak account existence. Apply the same normalization consistently across `core/sessions/localauth/orm.go`, `core/sessions/oidcauth/oidc.go`, and `core/sessions/ldapauth/ldap.go` local-fallback paths, and ensure `jsonAPIError` responses for `/sessions` don't propagate the raw underlying error text to unauthenticated clients.

### Proof of Concept
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"nonexistent@example.com","password":"wrongpassword"}
```
Response body contains `{"errors":[{"detail":"Invalid email"}]}` (401).

```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"knownvalid@example.com","password":"wrongpassword"}
```
Response body contains `{"errors":[{"detail":"Invalid password"}]}` (401).

The differing `detail` text confirms account existence, confirmable via the existing test fixture pattern at [7](#0-6) .

### Citations

**File:** core/web/auth/helpers.go (L15-23)
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

**File:** core/web/sessions_controller_test.go (L22-42)
```go
func TestSessionsController_Create(t *testing.T) {
	t.Parallel()
	ctx := t.Context()

	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	user := cltest.MustRandomUser(t)
	require.NoError(t, app.AuthenticationProvider().CreateUser(ctx, &user))

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	tests := []struct {
		name        string
		email       string
		password    string
		wantSession bool
	}{
		{"incorrect pwd", user.Email, "incorrect", false},
		{"incorrect email", "incorrect@test.net", cltest.Password, false},
		{"correct", user.Email, cltest.Password, true},
	}
```
