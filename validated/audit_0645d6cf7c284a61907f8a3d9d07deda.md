Found it. `SessionsController.Create` at `core/web/sessions_controller.go:56-60` passes through the raw error from `AuthenticationProvider().CreateSession` directly as the JSON API error body via `jsonAPIError(c, http.StatusUnauthorized, err)`. In the local auth implementation, `orm.CreateSession` at `core/sessions/localauth/orm.go:144-162` returns a distinct, distinguishable error string depending on whether the failure was due to an unrecognized email (`"Invalid email"`) versus a wrong password for a known email (`"Invalid password"`), and this distinction is returned unauthenticated, directly to the requesting client over `/sessions`.

### Title
User enumeration via distinct login error messages disclosed to unauthenticated clients - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `/sessions` login endpoint returns a different, attacker-observable error message depending on whether the submitted email exists in the system, allowing account enumeration analogous to the OMERO.web advisory's disclosure of user information during a credential-verification/password-reset-adjacent flow.

### Finding Description
`SessionsController.Create` (`core/web/sessions_controller.go:56-60`) is reachable without authentication (mounted under `unauth.POST("/sessions", sc.Create)` in `core/web/router.go:215`), and forwards whatever error is returned by `AuthenticationProvider().CreateSession` verbatim to the client: [1](#0-0) 

The local auth implementation `orm.CreateSession` distinguishes between an unknown/mismatched email and a wrong password with different error strings: [2](#0-1) 

Because the HTTP handler propagates `err.Error()` directly into the JSON API error response (`jsonAPIError`), an unauthenticated caller can distinguish "Invalid email" from "Invalid password" responses and thereby enumerate which email addresses are registered users on the node — this is exactly the class of "unnecessary user information disclosure" during a credential/account-recovery-adjacent operation described in the GHSA-gpmg-4x4g-mr5r advisory (differing responses leaking account existence).

### Impact Explanation
An unauthenticated attacker can enumerate valid admin/API user emails registered on a Chainlink node's web interface. While this doesn't grant direct access, it significantly aids follow-on credential-stuffing, phishing, or brute-force attacks against a known-valid set of accounts, and discloses account existence that node operators would reasonably expect to remain private, matching CWE-209 (Information Exposure Through an Error Message).

### Likelihood Explanation
The `/sessions` endpoint is intentionally public/unauthenticated to allow login, is rate-limited but not blocked (`rateLimiter` with `UnauthenticatedPeriod`/`Unauthenticated` limits per `core/web/router.go:207-215`), so an attacker can still enumerate over time. No special access or privilege is required — a single POST request with an arbitrary email is enough to observe the distinguishing message.

### Recommendation
Return a single generic error (e.g., "invalid credentials") for both the unknown-email and wrong-password cases in `orm.CreateSession`, keeping the differentiated audit events (`AuthLoginFailedEmail` / `AuthLoginFailedPassword`) only in internal logs/audit trail, not in the value returned to `SessionsController.Create`. Ensure `jsonAPIError` in the sessions controller for 401 responses uses a constant generic message rather than the raw provider error.

### Proof of Concept
```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"realuser@example.com","password":"wrongpassword"}
```
Response error body contains `"Invalid password"`.

```
POST /sessions HTTP/1.1
Content-Type: application/json

{"email":"nonexistent@example.com","password":"wrongpassword"}
```
Response error body contains `"Invalid email"` (or the underlying `FindUser` "no matching user" error surfaced through the same path). Comparing these two responses lets an unauthenticated client determine which email addresses are registered. [3](#0-2) [4](#0-3)

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
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

**File:** core/web/router.go (L207-216)
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
```

**File:** core/web/sessions_controller_test.go (L39-41)
```go
		{"incorrect pwd", user.Email, "incorrect", false},
		{"incorrect email", "incorrect@test.net", cltest.Password, false},
		{"correct", user.Email, cltest.Password, true},
```
