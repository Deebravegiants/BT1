### Title
Stale Cached Role in LDAP/OIDC Sessions and API Tokens Is Not Revoked When Upstream Role Changes - (File: core/sessions/oidcauth/oidc.go, core/sessions/ldapauth/ldap.go)

### Summary
The external report describes a pattern where a privileged identifier (`collector`/`additionalCollector`) is set once and never re-validated or reset when the underlying authority (lock ownership) changes, letting a de-authorized actor keep acting with old privileges. The same pattern exists in Chainlink's LDAP and OIDC authentication providers: a user's `role` is captured and persisted in a local cache table (`oidc_sessions`, `oidc_user_api_tokens`, `ldap_user_api_tokens`) at login/token-creation time, and subsequent authenticated requests only check whether that cached record has expired — they never re-verify the user's current upstream group membership/role.

### Finding Description
For OIDC, `AuthorizedUserWithSession` reads the cached `user_role` straight from `oidc_sessions` and only checks time-based expiry (`created_at + $2 >= now()`); it never re-queries the identity provider for the user's current claims/role. [1](#0-0) 

Likewise, `FindUserByAPIToken` for OIDC returns the `user_role` cached in `oidc_user_api_tokens` at token-creation time, gated only by an expiry check against `UserAPITokenDuration`. [2](#0-1) 

The LDAP provider has the identical pattern: `FindUserByAPIToken` returns the `user_role` cached in `ldap_user_api_tokens`, validated only by comparing `created_at + duration >= now()`, with no live re-check against the LDAP group membership. [3](#0-2) 

Both `role` values are consumed directly by the web authentication middleware to authorize the request as that role, with no additional freshness check: [4](#0-3) 

By contrast, `FindUser` (used for interactive session role checks outside of the cached-session path) for OIDC does re-query the local `users` table each time, but the cached-session/token paths above bypass this and rely purely on the value stored at issuance time.

This mirrors the reported bug class precisely: a privileged attribute (`role`, analogous to `collector`) is set once and is not reset/re-derived when the source of truth (LDAP group membership / OIDC claims, analogous to lock ownership) changes — the stale value continues to be honored until it expires naturally.

### Impact Explanation
If an administrator revokes or downgrades a user's role in the upstream LDAP/OIDC identity provider (e.g., removing them from the `Admin` group after an employee's access should be reduced), that user's already-issued session cookie or API token continues to grant the old (potentially `admin`) role for the full remainder of `SessionTimeout()` / `UserAPITokenDuration()`. This is a role-persistence/privilege-retention issue enabling continued unauthorized administrative actions (job management, key management, config changes) by a user whose authority was supposed to be revoked — directly analogous to the reported "previous owner can still collect fees" issue.

### Likelihood Explanation
This requires no attacker skill beyond simply continuing to use a session/token issued before role revocation — it is a passive, reliably-reachable condition any time an operator relies on LDAP/OIDC group changes to promptly restrict access. Because expiry windows (`UserAPITokenDuration`, `SessionTimeout`) are operator-configurable and can be long, the exposure window can be substantial.

### Recommendation
On every authenticated request (or at minimum periodically well inside the expiry window), re-validate the cached role against the current upstream LDAP group membership / OIDC claims rather than trusting the value cached at session/token creation. Alternatively, force re-authentication or role re-sync whenever an administrator explicitly changes a user's local role mapping, mirroring the `ClearNonCurrentSessions` purge already done in `localauth`'s `UpdateRole` for password/role changes. [5](#0-4) 

### Proof of Concept
1. Configure the node with LDAP or OIDC authentication, with a user mapped to the `Admin` group/claim.
2. User authenticates, receiving a session (`oidc_sessions` row) or generates an API token (`oidc_user_api_tokens` / `ldap_user_api_tokens` row) caching `user_role = admin`.
3. Administrator removes the user from the `Admin` LDAP group / OIDC claim (intending to downgrade to `view`).
4. The user continues to send requests using the existing session cookie or API token; `AuthorizedUserWithSession` / `FindUserByAPIToken` still return `Role: admin` because only the expiry timestamp is checked, not upstream group membership — the user retains admin-level access until the session/token naturally expires.

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L204-236)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the ldap_user_api_tokens table store
func (l *ldapAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (sessions.User, error) {
	if !l.config.UserApiTokenEnabled() {
		return sessions.User{}, errors.New("API token is not enabled ")
	}

	// Query the ldap user API token table for given token, user role and email are cached so
	// no further upstream LDAP query is performed, sessions and tokens are synced against the upstream server
	// via the UpstreamSyncInterval config and reaper.go sync implementation
	var foundUserToken struct {
		UserEmail string
		UserRole  sessions.UserRole
		Valid     bool
	}
	err := l.ds.GetContext(ctx, &foundUserToken,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_user_api_tokens WHERE token_key = $1",
		apiToken, l.config.UserAPITokenDuration().Duration(),
	)
	if err != nil {
		return sessions.User{}, err
	}
	if !foundUserToken.Valid { // API Token expired, purge
		if _, execErr := l.ds.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE token_key = $1", apiToken); execErr != nil {
			l.lggr.Errorf("error purging stale ldap API token session: %v", execErr)
		}
		return sessions.User{}, sessions.ErrUserSessionExpired
	}

	return sessions.User{
		Email: foundUserToken.UserEmail,
		Role:  foundUserToken.UserRole,
	}, nil
}
```

**File:** core/web/auth/auth.go (L75-112)
```go
// AuthenticateByToken authenticates a User by their API token.
//
// Implements authMethod
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```

**File:** core/sessions/localauth/orm.go (L259-296)
```go
// UpdateRole overwrites role field of the user specified by email.
func (o *orm) UpdateRole(ctx context.Context, email, newRole string) (sessions.User, error) {
	var userToEdit sessions.User

	if newRole == "" {
		return userToEdit, pkgerrors.New("user role must be specified")
	}

	err := sqlutil.TransactDataSource(ctx, o.ds, nil, func(tx sqlutil.DataSource) error {
		// First, attempt to load specified user by email
		if err := tx.GetContext(ctx, &userToEdit, "SELECT * FROM users WHERE lower(email) = lower($1)", email); err != nil {
			return pkgerrors.New("no matching user for provided email")
		}

		// Patch validated role
		userRole, err := sessions.GetUserRole(newRole)
		if err != nil {
			return err
		}
		userToEdit.Role = userRole

		_, err = tx.ExecContext(ctx, "DELETE FROM sessions WHERE email = lower($1)", email)
		if err != nil {
			o.lggr.Errorw("Failed to purge user sessions for UpdateRole", "err", err)
			return pkgerrors.New("error updating API user")
		}

		sql := "UPDATE users SET role = $1, updated_at = now() WHERE lower(email) = lower($2) RETURNING *"
		if err := tx.GetContext(ctx, &userToEdit, sql, userToEdit.Role, email); err != nil {
			o.lggr.Errorw("Error updating API user", "err", err)
			return pkgerrors.New("error updating API user")
		}

		return nil
	})

	return userToEdit, err
}
```
