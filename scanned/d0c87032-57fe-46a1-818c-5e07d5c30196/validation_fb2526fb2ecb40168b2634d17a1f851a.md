### Title
Stale cached role in LDAP/OIDC sessions and API tokens allows continued elevated access after upstream demotion - ([File: core/sessions/ldapauth/ldap.go], [File: core/sessions/ldapauth/sync.go], [File: core/sessions/oidcauth/oidc.go])

### Summary
The `FeeSplitter` bug class is: a per-account credit/entitlement value is cached at creation time and is never re-validated against the authoritative current state on every subsequent use — it is only refreshed by a narrow, specific code path (buy/sell), not universally. In the LDAP and OIDC `AuthenticationProvider` implementations, a user's `Role` is likewise cached in the `ldap_sessions` / `ldap_user_api_tokens` (and `oidc_sessions` / `oidc_user_api_tokens`) tables at session/token creation time, and every authenticated request (`AuthorizedUserWithSession`, `FindUserByAPIToken`) trusts that cached role directly instead of re-checking the upstream identity provider. Refreshing the cached role only happens via the separate `LDAPServerStateSyncer.Work()` job, which is disabled by default.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` and `FindUserByAPIToken` read `user_role` straight out of the local `ldap_sessions` / `ldap_user_api_tokens` tables without contacting the LDAP server: [1](#0-0) 

The comment even states the role "is cached so no further upstream LDAP query is performed." The same pattern exists for OIDC: [2](#0-1) [3](#0-2) 

The only mechanism that reconciles this cached role with the authoritative upstream group membership is `LDAPServerStateSyncer.Work`, which re-queries LDAP groups and issues `UPDATE ldap_sessions SET user_role = ...` / `UPDATE ldap_user_api_tokens SET user_role = ...` statements: [4](#0-3) [5](#0-4) 

Crucially, this sync job only runs automatically on an interval if `UpstreamSyncInterval` is configured to a non-zero value; by default it is `0s`, meaning periodic background reconciliation is entirely disabled and the sync is only invoked once at node startup: [6](#0-5) 

The documented default confirms this: [7](#0-6) 

This is the direct analog of the `FeeSplitter.onBalanceChange()` gap: the authoritative state (upstream LDAP group / OIDC role) changes, but the locally cached credential (`ldap_sessions.user_role`, `ldap_user_api_tokens.user_role`) that is used for every authorization decision is not updated on that state change — only on a narrow trigger (login/logout events implicitly calling `Work`, or an operator-enabled timer) that is off by default.

### Impact Explanation
If an administrator removes a user from the LDAP "Admin"/"Edit" group (or downgrades their OIDC-asserted role) to revoke elevated privileges, any session cookie or API token issued to that user *before* the demotion continues to authenticate with the old, stale, higher-privileged role for as long as that session/token remains valid (`SessionTimeout` / `UserAPITokenDuration`, up to 240h/10 days by default for API tokens) — because `AuthorizedUserWithSession`/`FindUserByAPIToken` never re-check the upstream source, and the reconciling sync job (`LDAPServerStateSyncer.Work`) does not run periodically unless an operator explicitly opts in via `UpstreamSyncInterval`. This is a concrete role/authorization bypass: a demoted or deactivated node operator retains admin-level API access (create/delete jobs, keys, bridges, etc.) on the Chainlink node well after their privileges were revoked upstream.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment using the LDAP or OIDC authentication provider (an explicitly supported, documented core-node auth mode) with default configuration, since `UpstreamSyncInterval = '0s'` is the documented default and requires no misconfiguration to trigger — it is simply the out-of-the-box behavior. The attack requires no code execution or malicious node behavior; it is triggered purely by normal admin operations (revoking a user's group membership) combined with the victim/attacker continuing to use a previously-issued, still-valid session or API token.

### Recommendation
Re-validate the user's role against the upstream identity provider (or at minimum force `LDAPServerStateSyncer.Work` / an OIDC-equivalent reconciliation) on every authenticated request, or bound the staleness window tightly and independent of `UpstreamSyncInterval` defaulting to disabled. At minimum, change the default so periodic sync is always enabled unless explicitly disabled, and immediately invalidate all cached sessions/tokens for a user whenever their upstream group/role membership is detected to have changed, rather than relying solely on TTL expiry.

### Proof of Concept
1. Configure the Chainlink node with `LDAPAuth` (or `OIDCAuth`) and leave `UpstreamSyncInterval` at its default (`'0s'`), disabling the periodic background sync.
2. User `alice@example.com` is a member of the LDAP `Admin` group. She logs in, creating a row in `ldap_sessions` with `user_role = 'admin'`, and/or generates an API token via `CreateAndSetAuthToken`, creating a row in `ldap_user_api_tokens` with `user_role = 'admin'` [8](#0-7) .
3. An operator removes Alice from the LDAP `Admin` group upstream, intending to revoke her admin access.
4. Because `UpstreamSyncInterval` is `0s`, no background job re-syncs `ldap_sessions`/`ldap_user_api_tokens`.
5. Alice continues to call authenticated endpoints using her still-valid session cookie or API token. `AuthorizedUserWithSession`/`FindUserByAPIToken` return `user_role = 'admin'` straight from the local cache [1](#0-0) , so she retains full admin privileges on the node until the session/token naturally expires (`SessionTimeout`/`UserAPITokenDuration`), even though she has been removed from the admin group upstream.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L342-373)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field. The state of the upstream LDAP server
// is polled and synced at the defined interval via a SleeperTask
func (l *ldapAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (sessions.User, error) {
	if len(sessionID) == 0 {
		return sessions.User{}, errors.New("session ID cannot be empty")
	}
	// Query the ldap_sessions table for given session ID, user role and email are cached so
	// no further upstream LDAP query is performed
	var foundSession struct {
		UserEmail string
		UserRole  sessions.UserRole
		Valid     bool
	}
	if err := l.ds.GetContext(ctx, &foundSession,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1",
		sessionID, l.config.SessionTimeout().Duration(),
	); err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	if !foundSession.Valid {
		// Sessions expired, purge
		if _, execErr := l.ds.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE id = $1", sessionID); execErr != nil {
			l.lggr.Errorf("error purging stale ldap session: %v", execErr)
		}
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	return sessions.User{
		Email: foundSession.UserEmail,
		Role:  foundSession.UserRole,
	}, nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L532-592)
```go
// CreateAndSetAuthToken generates a new credential token with the user role
func (l *ldapAuthenticator) CreateAndSetAuthToken(ctx context.Context, user *sessions.User) (*auth.Token, error) {
	newToken := auth.NewToken()

	err := l.SetAuthToken(ctx, user, newToken)
	if err != nil {
		return nil, err
	}

	return newToken, nil
}

// SetAuthToken updates the user to use the given Authentication Token.
func (l *ldapAuthenticator) SetAuthToken(ctx context.Context, user *sessions.User, token *auth.Token) error {
	if !l.config.UserApiTokenEnabled() {
		return errors.New("API token is not enabled ")
	}

	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return fmt.Errorf("LDAPAuth SetAuthToken hashed secret error: %w", err)
	}

	err = sqlutil.TransactDataSource(ctx, l.ds, nil, func(tx sqlutil.DataSource) error {
		// Is this user a local CLI Admin or upstream LDAP user?
		// Check presence in local users table. Set localauth_user column true if present.
		// This flag omits the session/token from being purged by the sync daemon/reaper.go
		isLocalCLIAdmin := false
		err = l.ds.QueryRowxContext(ctx, "SELECT EXISTS (SELECT 1 FROM users WHERE email = $1)", user.Email).Scan(&isLocalCLIAdmin)
		if err != nil {
			return fmt.Errorf("error checking user presence in users table: %w", err)
		}

		// Remove any existing API tokens
		if _, err = l.ds.ExecContext(ctx, "DELETE FROM ldap_user_api_tokens WHERE user_email = $1", user.Email); err != nil {
			return fmt.Errorf("error executing DELETE FROM ldap_user_api_tokens: %w", err)
		}
		// Create new API token for user
		_, err = l.ds.ExecContext(
			ctx,
			"INSERT INTO ldap_user_api_tokens (user_email, user_role, localauth_user, token_key, token_salt, token_hashed_secret, created_at) VALUES ($1, $2, $3, $4, $5, $6, now())",
			user.Email,
			user.Role,
			isLocalCLIAdmin,
			token.AccessKey,
			salt,
			hashedSecret,
		)
		if err != nil {
			return fmt.Errorf("failed insert into ldap_user_api_tokens: %w", err)
		}
		return nil
	})
	if err != nil {
		return errors.New("error creating API token")
	}

	l.auditLogger.Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	return nil
}
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

**File:** core/sessions/ldapauth/sync.go (L56-68)
```go
func (l *LDAPServerStateSyncer) Start(ctx context.Context) error {
	// If enabled, start a background task that calls the Sync/Work function on an
	// interval without needing an auth event to trigger it
	// Use IsInstant to check 0 value to omit functionality.
	if !l.config.UpstreamSyncInterval().IsInstant() {
		l.lggr.Info("LDAP Config UpstreamSyncInterval is non-zero, sync functionality will be called on a timer, respecting the UpstreamSyncRateLimit value")
		go l.run()
	} else {
		// Ensure upstream server state is synced on startup manually if interval check not set
		l.Work(ctx)
	}
	return nil
}
```

**File:** core/sessions/ldapauth/sync.go (L93-116)
```go
func (l *LDAPServerStateSyncer) Work(ctx context.Context) {
	// Purge expired ldap_sessions and ldap_user_api_tokens
	recordCreationStaleThreshold := l.config.SessionTimeout().Before(time.Now())
	err := l.deleteStaleSessions(ctx, recordCreationStaleThreshold)
	if err != nil {
		l.lggr.Error("unable to expire local LDAP sessions: ", err)
	}
	recordCreationStaleThreshold = l.config.UserAPITokenDuration().Before(time.Now())
	err = l.deleteStaleAPITokens(ctx, recordCreationStaleThreshold)
	if err != nil {
		l.lggr.Error("unable to expire user API tokens: ", err)
	}

	// Optional rate limiting check to limit the amount of upstream LDAP server queries performed
	if !l.config.UpstreamSyncRateLimit().IsInstant() {
		if !time.Now().After(l.nextSyncTime) {
			return
		}

		// Enough time has elapsed to sync again, store the time for when next sync is allowed and begin sync
		l.nextSyncTime = time.Now().Add(l.config.UpstreamSyncRateLimit().Duration())
	}

	l.lggr.Info("Begin Upstream LDAP provider state sync after checking time against config UpstreamSyncInterval and UpstreamSyncRateLimit")
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

**File:** docs/CONFIG.md (L777-781)
```markdown
### UpstreamSyncInterval
```toml
UpstreamSyncInterval = '0s' # Default
```
UpstreamSyncInterval is the interval at which the background LDAP sync task will be called. A '0s' value disables the background sync being run on an interval. This check is already performed during login/logout actions, all sessions and API tokens stored in the local ldap tables are updated to match the remote server
```
