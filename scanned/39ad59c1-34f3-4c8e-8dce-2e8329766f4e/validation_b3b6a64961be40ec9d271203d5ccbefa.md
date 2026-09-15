Confirmed: the OIDC authenticator has no upstream re-sync mechanism at all (only a session-expiry `reaper.go` that deletes stale rows by time, not a role-resync job like LDAP's `sync.go`). The comment in `FindUserByAPIToken` at `core/sessions/oidcauth/oidc.go:305-307` claims roles are "synced against the upstream server via the UpstreamSyncInterval config and reaper.go sync implementation" [1](#0-0)  — but this is factually false for OIDC: `reaper.go` only deletes expired rows by timestamp and never re-queries the identity provider or updates `user_role` [2](#0-1) . This is the discordant-cached-state class from the report: a "source of truth" (OIDC provider's ID-token group claims) is duplicated into local storage (`oidc_sessions.user_role`, `oidc_user_api_tokens.user_role`) and the two can drift apart with no reconciliation path.

### Title
Discordant/stale OIDC role caching in `oidc_sessions` and `oidc_user_api_tokens` with no upstream resync (privilege persists after downgrade) - ([File: core/sessions/oidcauth/oidc.go])

### Summary
The OIDC authenticator caches the RBAC role (`user_role`) derived from the identity provider's ID-token claims into the `oidc_sessions` table at login time (`handleTokenExchange`) and into `oidc_user_api_tokens` for API tokens. Unlike the LDAP driver, which has a dedicated background syncer (`core/sessions/ldapauth/sync.go`) that periodically re-queries the upstream directory and rewrites cached roles/purges stale sessions, the OIDC driver has no equivalent mechanism — its `reaper.go` only deletes expired rows by creation time. Once a session or API token is created, its cached role never changes until it expires naturally, even if the identity provider revokes/downgrades the user's group membership.

### Finding Description
`handleTokenExchange` maps the verified ID-token claims to a role once, then persists that role into `oidc_sessions`: [3](#0-2) 

Both `AuthorizedUserWithSession` and `FindUserByAPIToken` subsequently return the role stored at creation time from `oidc_sessions` / `oidc_user_api_tokens`, without re-verifying against the OIDC provider: [4](#0-3) [5](#0-4) 

The in-code comment explicitly (and incorrectly) claims this is safe because of an "UpstreamSyncInterval config and reaper.go sync implementation" — but `reaper.go` contains only a time-based deletion of stale sessions, with no role-resync logic at all, unlike the LDAP module's `LDAPServerStateSyncer.Work`, which explicitly re-queries group membership and rewrites `user_role` for existing `ldap_sessions`/`ldap_user_api_tokens` rows: [6](#0-5) 

This is the same bug class as the reported `managerFeeBPS` issue: a value (role/fee) is copied from an authoritative source into a secondary cache at a point in time, and that cache is trusted as if it were live truth, with the only actual chainlink-relevant fix path (background resync) missing for OIDC.

### Impact Explanation
If an OIDC-authenticated user's group membership is revoked or downgraded at the identity provider (e.g., removed from `NodeAdmins`), their existing chainlink node session or API token continues to be honored with the old, higher-privileged role (`Admin`/`Edit`/`Run`) for the full `SessionTimeout` / `UserAPITokenDuration` window (up to 240h by default) [7](#0-6) . This is a concrete role-bypass: an operator's decision to revoke access at the IdP is not honored by the node, leading to continued unauthorized privileged access to node APIs (job runs, key management, config changes) depending on role.

### Likelihood Explanation
Requires OIDC authentication to be enabled (`WebServer.AuthenticationMethod = 'oidc'` — an opt-in production configuration for enterprise access control) and an admin revoking access at the IdP side, expecting immediate effect. This is a plausible, realistic operational scenario (e.g., offboarding an employee) rather than a contrived edge case, and the vulnerability is 100% deterministic once triggered — no race condition needed.

### Recommendation
Add an OIDC upstream-state syncer analogous to `LDAPServerStateSyncer` (`core/sessions/ldapauth/sync.go`) that periodically re-verifies each active `oidc_sessions`/`oidc_user_api_tokens` entry's role against the identity provider (or, at minimum, purges/downgrades sessions when membership can no longer be confirmed), or drastically shorten cache lifetime and eliminate role caching by re-deriving role from a fresh provider check on each privileged request.

### Proof of Concept
1. Configure chainlink node with `WebServer.AuthenticationMethod = 'oidc'`, mapping the `NodeAdmins` claim group to Admin role.
2. User `alice@example.com` is a member of `NodeAdmins` at the IdP; she logs in via `/oidc/login` → `handleTokenExchange` inserts `oidc_sessions` row with `user_role = 'admin'` [8](#0-7) .
3. IdP admin removes alice from `NodeAdmins` (revokes admin access) — no chainlink-side action occurs.
4. Alice's browser session cookie (holding the old `oidc_sessions.id`) still resolves via `AuthorizedUserWithSession` to `Role: admin` until `SessionTimeout` (default 15m for cookie-idle, but no forced re-check) or, for API tokens, up to `UserAPITokenDuration` (default 240h) elapses [9](#0-8) .
5. Alice continues to perform admin-only operations on the node using the stale cached role, despite being revoked upstream.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L233-260)
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
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		c.String(http.StatusInternalServerError, "Error creating session")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L298-337)
```go
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

**File:** core/sessions/ldapauth/sync.go (L187-277)
```go
	// upstreamUserStateMap is now the most up to date source of truth
	// Now sync database sessions and roles with new data
	err = sqlutil.TransactDataSource(ctx, l.ds, nil, func(tx sqlutil.DataSource) error {
		// First, purge users present in the local ldap_sessions table but not in the upstream server
		type LDAPSession struct {
			UserEmail string
			UserRole  sessions.UserRole
		}
		var existingSessions []LDAPSession
		if err = tx.SelectContext(ctx, &existingSessions, "SELECT user_email, user_role FROM ldap_sessions WHERE localauth_user = false"); err != nil {
			return fmt.Errorf("unable to query ldap_sessions table: %w", err)
		}
		var existingAPITokens []LDAPSession
		if err = tx.SelectContext(ctx, &existingAPITokens, "SELECT user_email, user_role FROM ldap_user_api_tokens WHERE localauth_user = false"); err != nil {
			return fmt.Errorf("unable to query ldap_user_api_tokens table: %w", err)
		}

		// Create existing sessions and API tokens lookup map for later
		existingSessionsMap := make(map[string]LDAPSession)
		for _, sess := range existingSessions {
			existingSessionsMap[sess.UserEmail] = sess
		}
		existingAPITokensMap := make(map[string]LDAPSession)
		for _, sess := range existingAPITokens {
			existingAPITokensMap[sess.UserEmail] = sess
		}

		// Populate list of session emails present in the local session table but not in the upstream state
		emailsToPurge := []any{}
		for _, ldapSession := range existingSessions {
			if _, ok := upstreamUserStateMap[ldapSession.UserEmail]; !ok {
				emailsToPurge = append(emailsToPurge, ldapSession.UserEmail)
			}
		}
		// Likewise for API Tokens table
		apiTokenEmailsToPurge := []any{}
		for _, ldapSession := range existingAPITokens {
			if _, ok := upstreamUserStateMap[ldapSession.UserEmail]; !ok {
				apiTokenEmailsToPurge = append(apiTokenEmailsToPurge, ldapSession.UserEmail)
			}
		}

		// Remove any active sessions this user may have
		if len(emailsToPurge) > 0 {
			_, err = tx.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE user_email = ANY($1)", pq.Array(emailsToPurge))
			if err != nil {
				return err
			}
		}

		// Remove any active API tokens this user may have
		if len(apiTokenEmailsToPurge) > 0 {
			_, err = tx.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE user_email = ANY($1)", pq.Array(apiTokenEmailsToPurge))
			if err != nil {
				return err
			}
		}

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

		l.lggr.Info("local ldap_sessions and ldap_user_api_tokens table successfully synced with upstream LDAP state")
```

**File:** core/config/docs/core.toml (L228-233)
```text
# SessionTimeout determines the amount of idle time to elapse before session cookies expire. This signs out GUI users from their sessions.
SessionTimeout = '15m0s' # Default
# UserAPITokenEnabled enables the users to issue API tokens with the same access of their role
UserAPITokenEnabled = false # Default
# UserAPITokenDuration is the duration of time an API token is active for before expiring
UserAPITokenDuration = '240h0m0s' # Default
```
