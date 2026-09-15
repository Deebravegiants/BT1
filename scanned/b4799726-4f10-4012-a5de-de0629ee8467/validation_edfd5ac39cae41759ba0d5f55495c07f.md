## Title
Role/permission changes made in the external OIDC identity provider are not reflected in active chainlink node sessions or API tokens — ([File: core/sessions/oidcauth/oidc.go])

### Summary
The chainlink node's OIDC authentication provider (`core/sessions/oidcauth/oidc.go`) resolves and caches a user's RBAC role (`Admin`/`Edit`/`Run`/`View`) **once**, at the moment of login/token-exchange, by mapping the IdP's ID-token group claims to a role. That role is persisted into the `oidc_sessions` table (for browser sessions) or `oidc_user_api_tokens` table (for API tokens) and is never re-validated against the upstream identity provider for the lifetime of the session/token.

### Finding Description
During `handleTokenExchange`, the OIDC authenticator maps the verified ID-token claims to a role via `IDClaimsToUserRole` and stores it directly in the `oidc_sessions` row: [1](#0-0) 

Subsequent authenticated requests never re-check the IdP. `AuthorizedUserWithSession` simply selects the cached `user_role` column from `oidc_sessions` by session ID and validity/expiry timestamp — there is no call back to the OIDC provider to confirm the role/claims are still current: [2](#0-1) 

The same caching-without-revalidation pattern applies to API tokens created via `SetAuthToken`/`CreateAndSetAuthToken`, whose role is likewise frozen at creation time and read back verbatim in `FindUserByAPIToken`: [3](#0-2) [4](#0-3) 

The only background maintenance task for OIDC sessions, `sessionReaper` in `core/sessions/oidcauth/reaper.go`, purges rows purely by elapsed time (`created_at < before`) — it performs no upstream sync of role/group state: [5](#0-4) 

This is in stark contrast to the LDAP driver, which explicitly implements an upstream reconciliation loop (`LDAPServerStateSyncer.Work`) that re-queries the identity server on `UpstreamSyncInterval` and issues `UPDATE ldap_sessions SET user_role = ...` / purges sessions for users no longer present upstream: [6](#0-5) 

No equivalent syncer exists for the OIDC provider (`core/sessions/oidcauth/` has no `sync.go`), so an admin who is demoted or removed from the mapped Azure AD/OIDC group (e.g. `AdminClaim`/`EditClaim`/`RunClaim` groups configured in `[WebServer.OIDC]`) retains their previously-granted role in chainlink for the full remaining session/token lifetime, exactly mirroring the Rancher Azure AD advisory's root cause (permission changes not reflected on active sessions).

Downstream, every authorization gate (`RequiresAdminRole`, `RequiresEditRole`, GraphQL `authenticateUserIsAdmin`, etc.) trusts this stale cached role unconditionally: [7](#0-6) [8](#0-7) 

### Impact Explanation
An unprivileged actor is not required to exploit anything — this is a stale-permission retention bug affecting a legitimately-authenticated user whose privileges are revoked or lowered upstream. Any user with an active OIDC session cookie or previously-issued API key (`UserAPITokenDuration`, default `240h`) continues to exercise Admin/Edit/Run capabilities against the chainlink node — including creating jobs, managing bridges/external initiators, or extracting secrets via admin-only endpoints — even after their Azure AD/OIDC group membership is downgraded or removed. Because `UserAPITokenDuration` defaults to 10 days and `SessionTimeout` only governs idle-cookie expiry (not upstream revalidation), the exposure window is long and silent; there is no logout-forced re-check, and the only remediation is for the affected user to log out and log back in.

### Likelihood Explanation
This is deterministic, not probabilistic: any deployment with `WebServer.AuthenticationMethod = 'oidc'` enabled is affected by design — there is no code path in `oidcauth` that re-verifies claims after initial authentication. It requires only normal, expected admin operations (changing group membership in Azure AD/the OIDC IdP) to trigger; no attacker action against chainlink itself is needed.

### Recommendation
Implement an upstream reconciliation mechanism for the OIDC provider analogous to `ldapauth/sync.go`'s `LDAPServerStateSyncer`: periodically (or on each request) re-verify the ID token / re-query the IdP's userinfo/groups endpoint and update or purge `oidc_sessions` / `oidc_user_api_tokens` rows when the mapped role changes or group membership is lost, rather than trusting the role cached at token-exchange time indefinitely.

### Proof of Concept
1. Configure chainlink with `WebServer.AuthenticationMethod = 'oidc'` and `AdminClaim = 'NodeAdmins'` in `[WebServer.OIDC]`.
2. User `alice@example.com` is a member of the `NodeAdmins` Azure AD group; she logs in via the Rancher-style OIDC flow, hitting `handleTokenExchange`, which inserts `user_role = 'admin'` into `oidc_sessions`.
3. An operator removes alice from `NodeAdmins` in Azure AD (or downgrades her to a view-only group).
4. Using her still-valid session cookie (or a previously issued API key from `NewAPIToken`), alice continues to call admin-gated endpoints (e.g. `POST /v2/users` role change, job creation). `AuthorizedUserWithSession`/`FindUserByAPIToken` return the stale `admin` role from the database, and `RequiresAdminRole` grants access — despite alice no longer being an admin in the identity provider.
5. Access is only revoked if alice's session is naturally reaped by time (`SessionReaperExpiration`) or she manually logs out and back in.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L233-256)
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
```

**File:** core/sessions/oidcauth/oidc.go (L297-338)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the oidc_user_api_tokens table store
func (oi *oidcAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (clsessions.User, error) {
	if !oi.config.UserAPITokenEnabled() {
		return clsessions.User{}, errors.New("API token is not enabled")
	}

	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc user API token table for given token, user role and email are cached so
		// no further upstream OIDC query is performed, sessions and tokens are synced against the upstream server
		// via the UpstreamSyncInterval config and reaper.go sync implementation
		var foundUserToken struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundUserToken,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
			apiToken, oi.config.UserAPITokenDuration().Duration(),
		); err != nil {
			return err
		}
		if !foundUserToken.Valid {
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundUserToken.UserEmail,
			Role:  foundUserToken.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			// API Token expired, purge
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_user_api_tokens WHERE token_key = $1", apiToken); execErr != nil {
				oi.lggr.Errorf("error purging stale oidc API token session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
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

**File:** core/sessions/oidcauth/oidc.go (L510-548)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (oi *oidcAuthenticator) SetAuthToken(ctx context.Context, user *clsessions.User, token *auth.Token) error {
	if !oi.config.UserAPITokenEnabled() {
		return errors.New("API token is not enabled ")
	}

	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return fmt.Errorf("OIDCAuth SetAuthToken hashed secret error: %w", err)
	}

	err = sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Remove any existing API tokens
		if _, err = oi.ds.ExecContext(ctx, "DELETE FROM oidc_user_api_tokens WHERE user_email = $1", user.Email); err != nil {
			return fmt.Errorf("error executing DELETE FROM oidc_user_api_tokens: %w", err)
		}
		// Create new API token for user
		_, err = oi.ds.ExecContext(ctx,
			"INSERT INTO oidc_user_api_tokens (user_email, user_role, token_key, token_salt, token_hashed_secret, created_at) VALUES ($1, $2, $3, $4, $5, $6, now())",
			user.Email,
			user.Role,
			token.AccessKey,
			salt,
			hashedSecret,
		)
		if err != nil {
			return fmt.Errorf("failed insert into oidc_user_api_tokens: %w", err)
		}
		return nil
	})
	if err != nil {
		oi.lggr.Errorf("error creating API token: %v", err)
		return errors.New("error creating API token")
	}

	oi.auditLogger.Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	return nil
}
```

**File:** core/sessions/oidcauth/reaper.go (L37-50)
```go
func (sr *sessionReaper) Work(ctx context.Context) {
	recordCreationStaleThreshold := sr.config.SessionReaperExpiration().Before(
		sr.config.SessionTimeout().Before(time.Now()))
	err := sr.deleteStaleSessions(ctx, recordCreationStaleThreshold)
	if err != nil {
		sr.lggr.Error("unable to reap stale sessions: ", err)
	}
}

// DeleteStaleSessions deletes all sessions before the passed time.
func (sr *sessionReaper) deleteStaleSessions(ctx context.Context, before time.Time) error {
	_, err := sr.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE created_at < $1", before)
	return err
}
```

**File:** core/sessions/ldapauth/sync.go (L245-275)
```go
		// For each user session row, update role to match state of user map from upstream source
		var queryWhenClause strings.Builder
		emailValues := []any{}
		// Prepare CASE WHEN query statement with parameterized argument $n placeholders and matching role based on index
		for email, user := range upstreamUserStateMap {
			// Only build on SET CASE statement per local session and API token role, not for each upstream user value
			_, sessionOk := existingSessionsMap[email]
			_, tokenOk := existingAPITokensMap[email]
			if !sessionOk && !tokenOk {
				continue
			}
			emailValues = append(emailValues, email)
			fmt.Fprintf(&queryWhenClause, "WHEN user_email = $%d THEN '%s' ", len(emailValues), user.Role)
		}

		// If there are remaining user entries to update
		if len(emailValues) != 0 {
			// Set new role state for all rows in single Exec
			query := fmt.Sprintf("UPDATE ldap_sessions SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
			if err != nil {
				return err
			}

			// Update role of API tokens as well
			query = fmt.Sprintf("UPDATE ldap_user_api_tokens SET user_role = CASE %s ELSE user_role END", &queryWhenClause)
			_, err = tx.ExecContext(ctx, query, emailValues...)
			if err != nil {
				return err
			}
		}
```

**File:** core/web/auth/auth.go (L236-253)
```go
// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/resolver/auth.go (L45-55)
```go
// Authenticates the user from the session cookie and asserts has 'admin' role
func authenticateUserIsAdmin(ctx context.Context) error {
	session, ok := auth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return unauthorizedError{}
	}
	if session.User.Role != sessions.UserRoleAdmin {
		return RoleNotPermittedError{session.User.Role}
	}
	return nil
}
```
