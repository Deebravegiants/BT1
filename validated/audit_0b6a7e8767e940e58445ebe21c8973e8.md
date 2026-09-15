Confirmed missing `return` statement in `handleTokenExchange` at `core/sessions/oidcauth/oidc.go` lines 226-230. This is the strongest analog to the GoTrue advisory.

### Title
Missing return after email-claim validation failure creates an authenticated OIDC session with invalid/empty provider identity data - (File: core/sessions/oidcauth/oidc.go)

### Summary
In the OIDC login callback handler `handleTokenExchange`, when the identity provider's ID token claims do not contain a valid `email` field, the code logs an error and writes an HTTP 500 response but fails to `return`, allowing execution to continue and create a fully authenticated session using an empty/invalid email while still assigning a legitimate role derived from the (separately validated) group claims.

### Finding Description
`handleTokenExchange` extracts `email` from the verified ID token claims: [1](#0-0) 
When `claims["email"]` is missing or not a string, `ok` is `false`. The handler writes an internal server error response via `c.String(...)` but does **not** call `return`, unlike every other error branch in this same function which consistently calls `return` after writing an error response (see lines 167-172, 178-183, 189-196, 200-204, 208-212, 216-219, 221-225, 242-245). Execution therefore falls through with `email` set to the Go zero-value empty string, `""`.

The function proceeds to map the (separately extracted and validated) group claims to an RBAC role: [2](#0-1) 

It then inserts a new row into `oidc_sessions` using the empty `email` but the legitimately derived `role`, and completes the authentication flow by setting the session cookie and returning HTTP 200 with `Success: true` — even though an error response was already written to the same `gin.Context` earlier in the function: [3](#0-2) 

This session is later resolved by `AuthorizedUserWithSession`, which trusts the `user_email`/`user_role` columns verbatim to construct a `clsessions.User` used for all subsequent request authorization: [4](#0-3) 

This is a direct analog of GHSA-wpfr-6297-9v57: "a valid user object would have been created with invalid provider metadata." Here, a valid, role-bearing, authenticated session is created despite invalid (empty) identity data (`email`) from the provider, because the code path that should reject the request instead only logs and writes a body without aborting further processing.

### Impact Explanation
An authenticated session/user object is created with an empty `user_email` field but a real, usable RBAC role (Admin/Edit/Run/View, whichever the OIDC provider's group claims map to). Because `oidc_sessions.user_email` is empty, this session bypasses the notion of being tied to a specific identifiable user, and:
- `ClearNonCurrentSessions` looks up sessions by empty email and could interact with any other unrelated empty-email session rows.
- Audit logs record the login as an empty-string user (`audit.AuthLoginSuccessNo2FA` with `email: ""`), harming traceability.
- The session is fully functional for authorization purposes downstream (role-gated endpoints trust `clsessions.User.Role`), so a session created from malformed/incomplete provider data still grants working, role-scoped access to the node's admin API — an unintended and invalid identity/session object is produced and accepted by the system.

### Likelihood Explanation
This is reachable purely through the standard, unprivileged `/oidc-exchange` login callback flow (`ExtendRouter` registers it publicly): any client that completes the OAuth2 code exchange with the configured identity provider and receives an ID token lacking (or with a non-string) `email` claim — but still containing valid role/group claims — will trigger this path deterministically. This can occur due to IdP scope/config mismatches (e.g., `email` scope not granted while group claims are present) rather than requiring provider compromise, making it a plausible operational occurrence rather than a purely theoretical one.

### Recommendation
Add a `return` statement immediately after the `c.String(http.StatusInternalServerError, "Failed to get email from claims")` call at line 229 in `core/sessions/oidcauth/oidc.go`, mirroring every other error-handling branch in `handleTokenExchange`, so that the function aborts and does not create a session or issue a success response when the email claim cannot be extracted.

### Proof of Concept
1. Configure the OIDC authenticator per `core/services/chainlink/application.go` (`sessions.OIDCAuth`) against an identity provider that returns valid `groups`/role claims (e.g., matching `AdminClaim`) but omits the `email` claim (or returns a non-string value for it), e.g. due to a scope misconfiguration on the IdP side.
2. As an unprivileged client, perform the normal `/oidc-login` → provider auth → `/oidc-exchange` flow with `code`/`state` as usual.
3. Observe that `handleTokenExchange` logs `"Failed to get email from claims"` and writes a 500 body, but execution continues: `IDClaimsToUserRole` succeeds, a row is inserted into `oidc_sessions` with `user_email = ''` and the mapped role, the session cookie is set, and the final response is `HTTP 200 {"success": true}`.
4. Use the returned session cookie to call role-gated `/v2/...` endpoints; requests succeed and are authorized per `AuthorizedUserWithSession`'s lookup of the empty-email session row, confirming a working authenticated session was created from invalid provider identity data.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L226-230)
```go
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L233-245)
```go
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
```

**File:** core/sessions/oidcauth/oidc.go (L247-275)
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
