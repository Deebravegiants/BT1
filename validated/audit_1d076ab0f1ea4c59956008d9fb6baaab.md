Confirmed exactly as claimed in the code. Both error paths at lines 226-230 (`email` claim assertion failure) and lines 250-260 (`oidc_sessions` INSERT failure) write an HTTP error via `c.String(...)` but do not call `return`, so execution falls through to audit-logging a success, setting the session cookie, and returning `200 OK {"success": true}`. This is a genuine control-flow defect on an unauthenticated, client-reachable endpoint (`POST /oidc-exchange`, registered via `ExtendRouter` and mounted on the public API router group without prior auth middleware). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

Audit Report

## Title
Missing `return` after failed email-claim extraction and failed DB session persistence lets `handleTokenExchange` complete login with an unvalidated/unpersisted session - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `oidcAuthenticator.handleTokenExchange`, the email-claim type assertion failure (line 226-230) and the `oidc_sessions` INSERT failure (line 250-260) both write an HTTP 500 error body but omit `return`, allowing execution to fall through to audit-log a successful login, set a signed session cookie, and respond `200 OK {"success": true}`. This contradicts the intended fail-closed behavior demonstrated correctly elsewhere in the same function (e.g., the `ginSession.Save()` error path at lines 267-271, which does `return`).

## Finding Description
`POST /oidc-exchange` is registered in `ExtendRouter` [5](#0-4)  and mounted on the public `api` router group in `core/web/router.go` before any session-based auth middleware would apply to it — it's part of the login flow itself, so it must be reachable pre-authentication. After verifying the ID token signature and extracting role claims, the handler extracts `claims["email"]`; if it's not a string, it logs and writes an HTTP 500 body but doesn't return, so `email` remains `""` and execution continues into role mapping and session creation. Separately, if the `INSERT INTO oidc_sessions` call fails, the same pattern repeats: an HTTP 500 is written but the function proceeds anyway to unconditionally audit `AuthLoginSuccessNo2FA` and to `ginSession.Set(...)` / `ginSession.Save()`, ultimately writing a `200 OK` success response that overrides the earlier `c.String` write (since Gin doesn't halt on `c.String`/`c.JSON`, only `c.JSON`+`return` or `c.Abort()` do that). This means a signature-valid ID token from a misconfigured/malicious IdP that merely omits the `email` claim, or an ordinary transient DB failure, can produce a client-facing "success" response and a real signed session cookie whose backing DB row is either absent or has an empty `user_email`.

## Impact Explanation
This breaks the fail-closed guarantee of the authentication/session-creation code path on a client-facing, unauthenticated endpoint. It maps to the in-scope "node API authentication/session integrity" impact category: a client can end up with a cookie-backed session for a role-mapped identity while the code has already signaled a hard failure, and in the empty-email case, this could also produce cross-session key collisions in `oidc_sessions` (multiple logins sharing `user_email = ""`), which affects `ClearNonCurrentSessions`/session invalidation logic keyed on email.

## Likelihood Explanation
Triggering this requires only completing the standard, unauthenticated OIDC login/exchange flow that any client can initiate (`GET /oidc-login` → provider redirect → `POST /oidc-exchange`). The email-omission branch depends on the configured/attacker-controlled IdP's ID token content (still requires a valid signature, so not purely attacker-forged from the HTTP request), while the DB-insert-failure branch can occur on any transient database error, independent of attacker control. This is a real, reachable code defect, not a hypothetical one.

## Recommendation
Add `return` immediately after both error blocks (lines 229-230 and 259-260) to consistently abort the login flow, matching the pattern already used correctly at the `ginSession.Save()` error check (lines 267-271).

## Proof of Concept
1. Configure/point the node at an OIDC provider (or an intercepting proxy for one) whose ID token has a valid signature but omits the `email` claim while including a group claim matching `AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim`.
2. Perform `GET /oidc-login`, complete the provider round trip, then call `POST /oidc-exchange` with the resulting `code`/`state`.
3. Observe: `claims["email"].(string)` fails, `c.String(500, ...)` is called but no `return` occurs; execution continues, inserts a `oidc_sessions` row with `user_email=''`, sets the `webauth.SessionIDKey` cookie, and returns `200 OK {"success": true}`.
4. Alternatively, simulate/force a transient failure on the `INSERT INTO oidc_sessions` statement (e.g., DB restart mid-request in a test harness) and observe the same fall-through: cookie is set and `200 OK` returned despite no row being persisted, and subsequent use of that cookie against `AuthorizedUserWithSession` [6](#0-5)  fails with `ErrUserSessionExpired`, evidencing the inconsistent success response versus actual server state.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L247-262)
```go
	// Save new user authenticated clSession and role to oidc_sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	clSession := clsessions.NewSession()
	_, err = oi.ds.ExecContext(
		ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		clSession.ID,
		strings.ToLower(email),
		role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		c.String(http.StatusInternalServerError, "Error creating session")
	}

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})
```

**File:** core/sessions/oidcauth/oidc.go (L351-365)
```go
func (oi *oidcAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error) {
	if len(sessionID) == 0 {
		return clsessions.User{}, errors.New("session ID cannot be empty")
	}
	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc_sessions table for given session ID, user role and email are saved after the id claims is provided and validated
		var foundSession struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundSession,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_sessions WHERE id = $1",
			sessionID, oi.config.SessionTimeout().Duration(),
```

**File:** core/sessions/oidcauth/oidc.go (L658-663)
```go
func (oi *oidcAuthenticator) ExtendRouter(api *gin.RouterGroup) error {
	api.GET("/oidc-enabled", oi.handleCheckEnabled)
	api.GET("/oidc-login", oi.handleSignIn)
	api.POST("/oidc-exchange", oi.handleTokenExchange)

	return nil
```

**File:** core/web/router.go (L87-104)
```go
	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())

	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)

	err = app.AuthenticationProvider().ExtendRouter(api)
	if err != nil {
		return nil, err
	}
```
