The code exactly matches the reported claim. Both error branches in `handleTokenExchange` write an HTTP error response via `c.String()` but omit `return`, allowing the function to fall through to session creation/persistence and the final `200 OK` response.

Audit Report

## Title
Missing `return` after failed email-claim extraction and failed `oidc_sessions` DB insert lets `handleTokenExchange` complete login with an unvalidated/unpersisted session - ([File: core/sessions/oidcauth/oidc.go])

## Summary
In `oidcAuthenticator.handleTokenExchange`, the email-claim type assertion failure (line 226-230) and the `oidc_sessions` INSERT failure (line 250-260) both log an error and write an HTTP 500 body via `c.String()`, but neither branch includes a `return` statement. Since Gin does not halt handler execution on `c.String()`, execution falls through to audit logging, cookie session creation, and a final `200 OK {"success": true}` response, defeating the intended fail-closed behavior of these checks.

## Finding Description
`ExtendRouter` mounts `POST /oidc-exchange` on the public `api` router group with only session-cookie middleware and rate limiting, no auth requirement (as expected for a login endpoint): [1](#0-0) [2](#0-1) 

After ID token verification and role-claim extraction, the email claim is extracted with a type assertion; if it fails, an error is logged and written to the response, but there is no `return`: [3](#0-2) 

Execution continues into role mapping and session insertion using the empty `email` value. The DB insert error path has the same bug — no `return` after the error is logged/written: [4](#0-3) 

Immediately after, an unconditional success audit log is recorded, and the session cookie is set and saved, followed by a final `200 OK`: [5](#0-4) 

This is inconsistent with the correctly-guarded error path a few lines later (`ginSession.Save()` failure), which does `return` after writing its error: [6](#0-5) 

The downstream `AuthorizedUserWithSession` function trusts the `oidc_sessions` row keyed by session ID and email, confirming this table is the sole persistence/validation point being bypassed by the missing `return`: [7](#0-6) 

## Impact Explanation
This is a genuine authentication-integrity defect in the OIDC login/session-creation flow reachable by any client completing the standard OIDC redirect/exchange sequence (no privileged access required to reach the endpoint itself). The two missing `return`s cause the server to (a) issue a valid signed session cookie for a session that failed to be recorded in the database, or (b) issue a valid signed session cookie and persisted session tied to an empty-string `user_email` — while the server-side code path has already explicitly signaled a hard failure. This maps to the in-scope "node API authentication/session" impact class: the fail-closed guard for a security-relevant check is silently bypassed due to a control-flow bug, not a malicious peer/dependency/config issue.

## Likelihood Explanation
Reaching the code requires only the ordinary, unauthenticated OIDC exchange call (`GET /oidc-login` → provider redirect → `POST /oidc-exchange`), so no elevated credential is needed to reach the vulnerable code. Triggering the empty-email branch requires an ID token whose claims omit `email` (upstream/IdP-dependent, but a realistic misconfiguration or malicious/compromised IdP scenario, not requiring host or DB access by the attacker); triggering the DB-insert-failure branch requires a transient DB failure, which is plausible in production but not attacker-controlled on demand. Likelihood is moderate — the flaw is deterministic and always present, but the specific trigger conditions are partially outside pure client-request control.

## Recommendation
Add `return` immediately after both error blocks:
```go
email, ok := claims["email"].(string)
if !ok {
    oi.lggr.Errorf("Failed to get email from claims")
    c.String(http.StatusInternalServerError, "Failed to get email from claims")
    return
}
```
and
```go
_, err = oi.ds.ExecContext(ctx, "INSERT INTO oidc_sessions ...")
if err != nil {
    oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
    c.String(http.StatusInternalServerError, "Error creating session")
    return
}
```

## Proof of Concept
1. Configure/intercept an OIDC provider so its ID token omits the `email` claim but contains a valid group claim matching `AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim`.
2. Complete `GET /oidc-login` → provider redirect → `POST /oidc-exchange` with `{code, state}`.
3. In `handleTokenExchange`, `claims["email"].(string)` fails; `c.String(http.StatusInternalServerError, ...)` is written but execution continues.
4. A row is inserted into `oidc_sessions` with `user_email = ""` and the mapped role; the session cookie is set; the final response overwrites the 500 with `200 OK {"success": true}`.
5. Separately, a Go unit test can stub `oi.ds.ExecContext` to return an error and assert that despite the error, `ginSession.Save()` and the final `c.JSON(http.StatusOK, ...)` are still invoked — demonstrating the missing `return`.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L247-260)
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
```

**File:** core/sessions/oidcauth/oidc.go (L262-276)
```go
	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": email})

	// save session
	ginSession.Set(webauth.SessionIDKey, clSession.ID)
	err = ginSession.Save()
	if err != nil {
		oi.lggr.Errorf("failed to saved session %v", err)
		c.String(http.StatusInternalServerError, "Authentication failed")
		return
	}

	c.JSON(http.StatusOK, ExchangeTokenResponse{
		Success: true,
	})
}
```

**File:** core/sessions/oidcauth/oidc.go (L351-391)
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
		); err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return clsessions.ErrUserSessionExpired
			}
			return err
		}
		if !foundSession.Valid {
			// Sessions expired, purge
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundSession.UserEmail,
			Role:  foundSession.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L658-664)
```go
func (oi *oidcAuthenticator) ExtendRouter(api *gin.RouterGroup) error {
	api.GET("/oidc-enabled", oi.handleCheckEnabled)
	api.GET("/oidc-login", oi.handleSignIn)
	api.POST("/oidc-exchange", oi.handleTokenExchange)

	return nil
}
```

**File:** core/web/router.go (L77-104)
```go
	rl := config.WebServer().RateLimit()
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)

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
