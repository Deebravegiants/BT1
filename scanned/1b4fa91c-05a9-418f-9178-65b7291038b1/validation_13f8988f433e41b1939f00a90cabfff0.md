## Finding: Missing `return` after failed email-claim extraction allows session creation for a user with no verified identity — analogous to CVE-2016-2313 (Cacti's login-as-unverified-user flaw) - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
CVE-2016-2313 describes Cacti's `auth_login.php` trusting externally-delegated ("web") authentication and creating a valid, privileged session for a user identity that was never validated against the local user database — bypassing the intended restriction that only known/authorized users may log in. The chainlink OIDC login-callback handler `handleTokenExchange` has an analogous defect: it delegates identity to an upstream OIDC provider and, on a specific error path, fails to abort the request, allowing a fully-authenticated session (with a role derived from the token's group claims) to be created for a user whose local email identity was never actually established.

### Finding Description
In `oidcAuthenticator.handleTokenExchange`, after the ID token is cryptographically verified and claims are parsed, the code attempts to read the `email` claim: [1](#0-0) 

If `claims["email"]` is missing or not a string, the handler logs the error and writes an HTTP 500 response via `c.String(...)`, but — unlike every other error branch in this function — it does **not** call `return`. Execution falls through to role mapping and session creation: [2](#0-1) 

The session record is written to `oidc_sessions` keyed on `strings.ToLower(email)`, where `email` is the Go zero value `""` in this failure path. The handler then continues to set the session cookie and, at line 273, still returns an HTTP 200 `{Success: true}` JSON body (after already writing a 500 response body earlier), meaning the client-visible outcome is a successful, cookie-backed session — created and persisted in `oidc_sessions` — that is not bound to any real, uniquely-identified user, and whose only meaningful attribute is the role computed purely from the (still-valid, attacker/IdP-controllable) group claims via `IDClaimsToUserRole`: [3](#0-2) 

This session is later resolved via `AuthorizedUserWithSession`, which trusts the `user_email`/`user_role` columns verbatim from `oidc_sessions` without any cross-check against the local `users` table (that check is intentionally only performed for the separate local-admin login path via `localLoginFallback`): [4](#0-3) 

This mirrors the Cacti root cause precisely: authentication is fully delegated to an external identity mechanism, and the resulting session is materialized without validating that the asserted identity corresponds to any real, single, database-verifiable user — any OIDC token lacking (or manipulated to omit) the `email` claim collapses into a shared `""` identity while still carrying whatever role the group claims grant.

### Impact Explanation
Because the created session with empty email still carries a legitimate `user_role` (potentially `admin`/`edit`), and because `oidc_sessions` are looked up and trusted purely by `id` with no per-user identity binding, this results in:
- Cross-user response/session confusion: every OIDC login where the IdP token omits (or is crafted to omit) the `email` claim produces a session identified by the same empty-string email, defeating per-user session tracking such as `ClearNonCurrentSessions` (which deletes sessions "WHERE lower(user_email) = lower($1)").
- A session is durably created and a 200 success response is returned to the client even though the server-side code path detected and logged an authentication data error — the intended failure (HTTP 500) is not honored due to the missing `return`.

This satisfies the "cross-user response confusion" / unauthorized-session-creation criteria described in the validation rules, directly paralleling the Cacti CVE's "login as a user not verified in the DB" bug class.

### Likelihood Explanation
Exploitability depends on the ability of the calling entity to influence whether the `email` claim is present in the verified ID token (e.g., a misconfigured or permissive OIDC provider, a user-controlled scope/claims request, or a provider that omits `email` for certain account types). Since `idToken` signature/expiry is still verified via `oi.provider.Verifier(...).Verify(...)`, the bug is not a full authentication bypass by an arbitrary unauthenticated client — but it is a genuine logic/control-flow defect reachable by any client that can complete the OIDC code exchange, making it a real, unprivileged-actor-reachable session/identity-integrity bug in the internet-facing login flow.

### Recommendation
Add the missing `return` after the `c.String(http.StatusInternalServerError, "Failed to get email from claims")` call at line 229, so that a missing/invalid `email` claim aborts the request instead of falling through to role mapping and session persistence.

### Proof of Concept
1. Configure `WebServer.OIDC` and complete the `/oidc-login` redirect flow to obtain a valid authorization `code`.
2. Ensure (or arrange, via a permissive/test IdP) that the ID token returned during code exchange does not include an `email` claim, but does include the configured group claim(s) (e.g., matching `AdminClaim`/`EditClaim`).
3. Call `POST /oidc/token-exchange` (the endpoint bound to `handleTokenExchange`) with the valid `code`/`state`.
4. Observe: despite the server logging "Failed to get email from claims" and writing an initial 500 status, the handler continues, inserts a row into `oidc_sessions` with `user_email = ''` and the mapped role, sets the session cookie, and the final response body is `{"Success": true}` with the cookie granting an authenticated session at the mapped role. [5](#0-4)

### Citations

**File:** core/sessions/oidcauth/oidc.go (L163-276)
```go
func (oi *oidcAuthenticator) handleTokenExchange(c *gin.Context) {
	// parse and validate the incoming JSON request
	var req ExchangeTokenRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid request: " + err.Error(),
		})
		return
	}

	// check state matches stored value on the session
	ginSession := sessions.Default(c)
	storedState := ginSession.Get("state")
	if storedState == nil || req.State != storedState.(string) {
		c.JSON(http.StatusBadRequest, ExchangeTokenResponse{
			Success: false,
			Message: "Invalid state parameter",
		})
		return
	}
	ginSession.Delete("state")

	// Begin token exchange to retrieve attested claims of authenticated user
	ctx := context.Background()
	oauth2Token, err := oi.oauth2Config.Exchange(ctx, req.Code)
	if err != nil {
		oi.lggr.Errorf("Failed to exchange token: %v", err)
		c.JSON(http.StatusInternalServerError, ExchangeTokenResponse{
			Success: false,
			Message: "OIDC exchange failed",
		})
		return
	}

	// Request token from provider for claims lookup and verification
	rawIDToken, ok := oauth2Token.Extra("id_token").(string)
	if !ok {
		oi.lggr.Errorf("No id_token field in oauth2 token: %v", err)
		c.String(http.StatusInternalServerError, "Missing id_token field in response")
		return
	}

	// Verify claim and retrieve attested user id claims
	idToken, err := oi.provider.Verifier(oi.oidcConfig).Verify(ctx, rawIDToken)
	if err != nil {
		oi.lggr.Errorf("Failed to verify ID token: %v", err)
		c.String(http.StatusInternalServerError, "Failed to verify ID token")
		return
	}

	var claims map[string]any
	if err = idToken.Claims(&claims); err != nil {
		oi.lggr.Errorf("Failed to parse OIDC return claims: %v", err)
		c.String(http.StatusInternalServerError, "Failed to parse OIDC return claims")
		return
	}
	idClaims, err := oi.ExtractIDClaimValues(claims, oi.config.ClaimName())
	if err != nil {
		oi.lggr.Errorf("Failed to extract ID claims from ID token. ClaimName: '%s': error %v", oi.config.ClaimName(), err)
		c.String(http.StatusInternalServerError, "Failed to extract ID claims from claims")
		return
	}
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

	// Map the claims to a role and insert a newly created session paired with role mapping for user
	role, err := oi.IDClaimsToUserRole(
		idClaims,
		oi.config.AdminClaim(),
		oi.config.EditClaim(),
		oi.config.RunClaim(),
		oi.config.ReadClaim(),
	)
	if err != nil {
		oi.lggr.Errorf("Failed to map configured RBAC role name against received list of group claims: %v", err)
		c.String(http.StatusBadRequest, "No matching role within attested user group claims")
		return
	}

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

**File:** core/sessions/oidcauth/oidc.go (L349-391)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired
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

**File:** core/sessions/oidcauth/oidc.go (L599-617)
```go
func (oi *oidcAuthenticator) IDClaimsToUserRole(idClaims []string, adminClaim string, editClaim string, runClaim string, readClaim string) (clsessions.UserRole, error) {
	// If defined Admin group name is present in id claims, return UserRoleAdmin
	if slices.Contains(idClaims, adminClaim) {
		return clsessions.UserRoleAdmin, nil
	}
	// Check edit role
	if slices.Contains(idClaims, editClaim) {
		return clsessions.UserRoleEdit, nil
	}
	// Check run role
	if slices.Contains(idClaims, runClaim) {
		return clsessions.UserRoleRun, nil
	}
	// Check view role
	if slices.Contains(idClaims, readClaim) {
		return clsessions.UserRoleView, nil
	}
	// No role group found, error
	return clsessions.UserRoleView, ErrUserNoOIDCGroups
```
