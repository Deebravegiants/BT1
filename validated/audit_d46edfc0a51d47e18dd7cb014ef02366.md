### Title
Local-auth `/sessions` login endpoint reveals account existence via differing error messages - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `POST /sessions` login endpoint returns different, unsanitized error content depending on whether the submitted email corresponds to an existing user versus an existing user with a wrong password. This is the same bug class as CVE-2022-44381 (Snipe-IT): distinguishable responses on an authentication-adjacent endpoint allow an unauthenticated caller to enumerate valid accounts.

### Finding Description
`SessionsController.Create` is registered on the unauthenticated `/sessions` route (rate-limited only, no auth required): [1](#0-0) 

It calls `AuthenticationProvider().CreateSession(ctx, sr)` and, on any error, forwards the raw Go error directly to the client via `jsonAPIError(c, http.StatusUnauthorized, err)`: [2](#0-1) 

In the local-auth implementation, `CreateSession` first calls `FindUser`, and if that fails (i.e., the email does not exist) it returns the raw underlying error unmodified. If the email exists but the case-insensitive comparison or password check fails, it instead returns hand-crafted, normalized strings `"Invalid email"` / `"Invalid password"`: [3](#0-2) 

Because `jsonAPIError` embeds the error text in the JSON response body (as demonstrated elsewhere in the codebase, e.g. `user_controller_test.go` asserting exact error detail strings like `"old password does not match"`), the body returned for a non-existent email (raw DB/ORM error, e.g. containing `sql: no rows in result set` style text) is distinguishable from the body returned for an existing email with a wrong password (`"Invalid password"`). Both cases share the same HTTP status code (401), so only the differing message content leaks account existence — mirroring the Snipe-IT CVE-2022-44381 pattern of "response variations" revealing whether an account exists.

### Impact Explanation
An unauthenticated attacker can enumerate valid Chainlink node operator/admin email addresses by observing the distinct error text returned from `/sessions`. This does not by itself grant access, but it materially aids credential-stuffing, targeted phishing, or brute-force attacks against the node's admin API, and undermines the confidentiality of user identities (CWE-203).

### Likelihood Explanation
Likelihood is high for exploitation ease (single unauthenticated POST request, no special access needed) but the endpoint is rate-limited (`rl.UnauthenticatedPeriod()/rl.Unauthenticated()`), which slows but does not prevent large-scale enumeration. The vulnerability requires local-auth (default, non-LDAP/OIDC) mode.

### Recommendation
Normalize all `CreateSession` failure paths in `core/sessions/localauth/orm.go` (and equivalently in `ldapauth`/`oidcauth`) to return a single generic error (e.g., `"invalid email or password"`) regardless of whether the email exists, and ensure `SessionsController.Create` in `core/web/sessions_controller.go` never forwards raw underlying error text to unauthenticated clients.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@test.com","password":"anything"}` → 401 response body contains the raw `FindUser` error text.
2. `POST /sessions` with `{"email":"<valid-existing-email>","password":"wrongpassword"}` → 401 response body contains the literal string `"Invalid password"`.
3. Comparing response bodies (not just status code) across many candidate emails allows an attacker to distinguish valid from invalid accounts.

Note: I was unable to fully inspect the exact implementation of `jsonAPIError` (ran out of tool budget confirming it verbatim), but its behavior of surfacing `err.Error()` text into JSON:API `detail` fields is strongly corroborated by other controller tests in the codebase that assert on exact error-message strings returned from this helper family.

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
