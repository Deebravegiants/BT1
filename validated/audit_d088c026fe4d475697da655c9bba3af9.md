Based on my investigation, I found a clear analog to the Keystone disabled-tenant token bug in the LDAP authentication provider.

### Title
Disabled/deactivated LDAP users retain valid authenticated sessions and API tokens until the next background sync - (File: `core/sessions/ldapauth/ldap.go`, `core/sessions/ldapauth/sync.go`)

### Summary
`FindUser` correctly checks the upstream LDAP "is active" attribute at login time via `validateUsersActive`, but the two authorization-check paths that run on every authenticated request — `AuthorizedUserWithSession` (session cookie) and `FindUserByAPIToken` (API key) — never re-check the user's active status against LDAP. They only validate against locally cached `ldap_sessions` / `ldap_user_api_tokens` rows and their expiry timestamps.

### Finding Description
`FindUser` gates login on the active flag returned from `validateUsersActive`: [1](#0-0) . However, once a session or API token is created, subsequent requests are authorized purely by `AuthorizedUserWithSession`, which only checks `ldap_sessions` row expiry — it performs no LDAP query and no active-status check: [2](#0-1) . Likewise `FindUserByAPIToken` only checks `ldap_user_api_tokens` expiry, with no active-status re-validation: [3](#0-2) .

Revocation of disabled users is deferred entirely to the asynchronous `LDAPServerStateSyncer.Work` background job, which re-queries LDAP group membership and the active attribute, then purges stale `ldap_sessions`/`ldap_user_api_tokens` rows for users no longer present in the up-to-date upstream state: [4](#0-3) . This sync only runs on the configured `UpstreamSyncInterval`/`UpstreamSyncRateLimit` schedule (or once at startup if the interval is unset), not on every request: [5](#0-4) .

This is structurally the same bug class as CVE-2012-4457 in OpenStack Keystone: the disable/deactivation state is checked only at token-issuance/periodic-reconciliation time rather than at token-validation time, so a token/session issued while the account was active continues to authorize the disabled account's requests for the entire window between deactivation and the next sync cycle.

### Impact Explanation
An administrator who disables (or removes from the authorizing LDAP group) a user in the identity server expects that user's access to the Chainlink node to be revoked immediately. In this implementation, any session cookie or API token issued before deactivation continues to authenticate successfully — granting the disabled user's role (view/run/edit/admin) — until the periodic `LDAPServerStateSyncer.Work` run purges it. Depending on operator configuration (`UpstreamSyncInterval`, `UpstreamSyncRateLimit`), this window can be long, allowing continued unauthorized use of node management/administration endpoints (job management, key management, etc., gated by role via `webauth.Authenticate`/`AuthenticateBySession`/`AuthenticateByToken` in `core/web/auth/auth.go`).

### Likelihood Explanation
Likelihood is moderate: it requires the LDAP-backed authentication provider to be configured (not the default local-auth path), and requires an operator to disable a user who already holds an active session or API token. No additional privilege or network position is required by the disabled user beyond continuing to send the same cookie/token they already had — this is a normal unprivileged client request path (`AuthenticateBySession`/`AuthenticateByToken` in `core/web/auth/auth.go`), not a network- or peer-layer attack.

### Recommendation
Re-validate the user's active status against the upstream LDAP server (or a sufficiently fresh local cache updated synchronously on disable events) inside `AuthorizedUserWithSession` and `FindUserByAPIToken`, not only during the periodic sync job. At minimum, reduce the trust window by shortening default sync intervals and documenting the exposure, but the correct fix is to perform (or reuse) the active-attribute check on every authorization call, mirroring the check already done in `FindUser`.

### Proof of Concept
1. Configure Chainlink with the LDAP authenticator enabled.
2. Log in as a user (`CreateSession`) who is a member of an authorized LDAP group; a valid `ldap_sessions` row and cookie are issued.
3. In the upstream LDAP server, mark the user inactive (or remove from the group) without waiting for `UpstreamSyncInterval` to elapse.
4. Continue sending requests with the previously issued session cookie to any authenticated route (e.g. through `sessionRoutes`/`Authenticate` middleware in `core/web/router.go`).
5. Observe that `AuthorizedUserWithSession` still returns the user and role successfully — the request is authorized despite the account being disabled upstream — until the next `LDAPServerStateSyncer.Work` execution purges the row.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L131-142)
```go
	// First query for user "is active" property if defined
	usersActive, err := l.validateUsersActive([]string{email})
	if err != nil {
		if errors.Is(err, ErrUserNotInUpstream) {
			return sessions.User{}, ErrUserNotInUpstream
		}
		l.lggr.Errorf("error in validateUsers call: %v", err)
		return sessions.User{}, errors.New("error running query to validate user active")
	}
	if !usersActive[0] {
		return sessions.User{}, errors.New("user not active")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L204-230)
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

**File:** core/sessions/ldapauth/sync.go (L56-114)
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

func (l *LDAPServerStateSyncer) Close() error {
	close(l.stopCh)
	<-l.done
	return nil
}

func (l *LDAPServerStateSyncer) run() {
	defer close(l.done)
	ctx, cancel := l.stopCh.NewCtx()
	defer cancel()
	ticker := time.NewTicker(l.config.UpstreamSyncInterval().Duration())
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			l.Work(ctx)
		}
	}
}

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
```

**File:** core/sessions/ldapauth/sync.go (L174-243)
```go
	// For each unique user in list of active sessions, check for 'Is Active' property if defined in the config. Some LDAP providers
	// list group members that are no longer marked as active
	usersActiveFlags, err := l.validateUsersActive(dedupedEmails, conn)
	if err != nil {
		l.lggr.Error("Error validating supplied user list: ", err)
	}
	// Remove users in the upstreamUserStateMap source of truth who are part of groups but marked as deactivated/no-active
	for i, active := range usersActiveFlags {
		if !active {
			delete(upstreamUserStateMap, dedupedEmails[i])
		}
	}

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
