### Title
Stale LDAP session/API-token role caching allows revoked or demoted users to retain elevated privileges until the next upstream sync - ([File: core/sessions/ldapauth/ldap.go], [File: core/sessions/ldapauth/sync.go])

### Summary
The LDAP authentication provider caches a user's role in the local `ldap_sessions` and `ldap_user_api_tokens` tables at login/token-creation time and never re-validates that role against the upstream LDAP server on subsequent requests. Reconciliation only happens via a background `LDAPServerStateSyncer.Work` loop gated by `UpstreamSyncInterval`, which **defaults to `0s` ("instant")** and in that mode only runs once at node startup, never again. This mirrors the oracle staleness bug class in the source report: a stale, cached state ("lastPrice"/role) can be relied upon by an actor who knows an authoritative update (an oracle price update / an LDAP role revocation) is imminent or has already happened upstream, letting them keep acting under the old, now-incorrect state for the entire staleness window.

### Finding Description
`ldapAuthenticator.AuthorizedUserWithSession` and `ldapAuthenticator.FindUserByAPIToken` both read the cached `user_role` column directly from the local database and return it as-is, without querying the upstream LDAP server: [1](#0-0) [2](#0-1) 

The package-level doc comment claims "This sync happens for every auth endpoint hit, and via the defined sync interval," but no such per-request sync call exists in either `AuthorizedUserWithSession` or `FindUserByAPIToken`: [3](#0-2) 

Reconciliation is performed exclusively by `LDAPServerStateSyncer.Work`, invoked on a ticker at `UpstreamSyncInterval`. If `UpstreamSyncInterval` `IsInstant()` (its default `0s`), the syncer only calls `Work` once at `Start` and never schedules the background ticker: [4](#0-3) 

`Work` is what purges sessions/tokens for deactivated users and downgrades roles for demoted users by diffing against `upstreamUserStateMap`: [5](#0-4) 

Combined with default long-lived credentials — `SessionTimeout = '15m'` for GUI sessions but `UserAPITokenDuration = '240h0m0s'` (10 days) for API tokens — a user demoted from Admin to a lower role, or fully deactivated, upstream in LDAP retains their originally-cached Admin/Edit role in `ldap_user_api_tokens` for up to 10 days by default if `UpstreamSyncInterval` is left at its default value: [6](#0-5) 

This is the direct analog of the reported bug class: the trusted authoritative source (LDAP directory / oracle price) has updated, but the consuming system continues to authorize actions (privileged API calls / avoiding liquidation) using the stale cached value ("lastUpdateTimestamp" / cached `user_role`) for a configurable timeout window that, by default, never actually elapses.

### Impact Explanation
An Admin/Edit-role user who is demoted or deactivated in the upstream LDAP directory (e.g., due to termination, compromise, or policy enforcement) continues to be treated by the chainlink node as holding their old privileged role for the entire `UserAPITokenDuration` (up to 10 days by default) or until a manual restart, because the default `UpstreamSyncInterval = '0s'` never triggers periodic reconciliation. This allows continued unauthorized privileged actions (job creation/deletion, key management, bridge configuration, etc.) via `RequiresAdminRole`/`RequiresEditRole`-gated endpoints, using a credential that should already be revoked — a concrete authentication/role bypass.

### Likelihood Explanation
This requires the LDAP authentication method to be enabled (`WebServer.AuthenticationMethod = 'ldap'`) and relies on operators leaving `UpstreamSyncInterval` at its documented default of `0s`, which is the out-of-the-box configuration per `docs/CONFIG.md`. No malicious/insider LDAP-server behavior is needed — an operator simply removing/demoting a user from the LDAP group is a completely ordinary, expected admin operation, and the already-issued token/session for that user silently continues to function with the old role.

### Recommendation
- Re-validate the cached role against a short-lived check (or force a sync) on every privileged-role-gated request, not just at a periodic interval, at minimum for `FindUserByAPIToken` and `AuthorizedUserWithSession`.
- Change the default `UpstreamSyncInterval` to a bounded, non-zero value (e.g., minutes) rather than `0s`/"instant", and document clearly that `0s` means "sync only at startup, never again" rather than "sync every request" as the current package doc comment states.
- Reduce the default `UserAPITokenDuration` or require re-validation against LDAP before honoring high-privilege actions from a cached API token.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'` and leave `WebServer.LDAP.UpstreamSyncInterval` at its default (`0s`).
2. An LDAP Admin-group user logs in via `CreateSession`, receiving a cached `ldap_sessions`/`ldap_user_api_tokens` row with `user_role = 'admin'`.
3. LDAP directory admin removes the user from the Admin group (or deactivates the account) — a normal, legitimate upstream operation.
4. Because `UpstreamSyncInterval.IsInstant()` is true, `LDAPServerStateSyncer.Work` (see `core/sessions/ldapauth/sync.go:56-68`) never runs again after node startup.
5. The revoked user continues calling Admin-role-gated endpoints using their still-valid API token (`FindUserByAPIToken`, `core/sessions/ldapauth/ldap.go:204-236`) for up to `UserAPITokenDuration` (240h by default), performing privileged actions despite being demoted/removed upstream.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L12-18)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function

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

**File:** core/sessions/ldapauth/sync.go (L187-243)
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
```

**File:** docs/CONFIG.md (L661-662)
```markdown
UserAPITokenDuration is the duration of time an API token is active for before expiring

```
