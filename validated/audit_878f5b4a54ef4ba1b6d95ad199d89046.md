### Title
LDAP-authenticated user retains stale role/access after upstream demotion, deletion, or deactivation until the periodic sync interval elapses - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The LDAP authentication provider caches a user's role in the local `ldap_sessions` and `ldap_user_api_tokens` tables at login time, and `AuthorizedUserWithSession`/`FindUserByAPIToken` trust this cached role on every subsequent request without re-checking the upstream LDAP server. Revocation of admin rights (role downgrade, group removal, account deactivation, or deletion from the LDAP directory) is only propagated by a background `LDAPServerStateSyncer.Work` job that runs on a fixed interval (`UpstreamSyncInterval`). This mirrors the CVE-2021-31590 bug class: a previously-privileged token/session keeps working with elevated access after the backing account's privilege is revoked, until the token naturally expires or (here) a background sync catches up.

### Finding Description
`AuthorizedUserWithSession` in `core/sessions/ldapauth/ldap.go` only reads the cached role from the `ldap_sessions` table and checks expiry against `SessionTimeout` — it never re-queries the LDAP server: [1](#0-0) 

Similarly `FindUserByAPIToken` trusts the cached role in `ldap_user_api_tokens` and states explicitly that "no further upstream LDAP query is performed": [2](#0-1) 

The package-level doc comment claims sync happens "for every auth endpoint hit, and via the defined sync interval," but the actual per-request auth path (`AuthorizedUserWithSession`, `FindUserByAPIToken`) contains no upstream LDAP call — reconciliation with the upstream directory only happens through the separate `LDAPServerStateSyncer.Work` function, invoked on a ticker (`l.config.UpstreamSyncInterval()`), not per request: [3](#0-2) [4](#0-3) [5](#0-4) 

The `Work` function is the only place that purges sessions/tokens for users removed from the upstream group mapping and downgrades/upgrades roles for existing sessions and tokens: [6](#0-5) 

Because this reconciliation is asynchronous and interval-based rather than enforced at authentication time, a user who has already authenticated and cached an `admin` role in `ldap_sessions`/`ldap_user_api_tokens` retains that role for every request made in the window between the upstream revocation and the next scheduled `Work()` run — directly analogous to the PwnDoc JWT issue where a downgraded/deleted user retained admin access because the authorization check trusted stale token/session state instead of re-validating against current authoritative state.

### Impact Explanation
If an operator demotes an admin to a lower role, disables/deactivates a user, or removes them from the LDAP directory entirely, that user's existing session cookie and any previously-issued API token continue to grant the old (potentially `admin`) privileges against the node's HTTP/GraphQL API — including admin-only endpoints such as user management (`RequiresAdminRole`) — for up to the configured `UpstreamSyncInterval` window. This is a genuine access-control bypass in the node's authentication/authorization path reachable by an already-authenticated but subsequently de-privileged actor, potentially allowing continued fund-affecting job/administrative operations after intended revocation.

### Likelihood Explanation
This requires an operator using the LDAP authentication provider (`AuthenticationProviderName = LDAPAuth`) and depends on `UpstreamSyncInterval` being non-zero (if zero/instant, `Work` runs synchronously on every check per the `Start` logic, closing the window — see `core/sessions/ldapauth/sync.go:56-67`). For any non-zero interval, the exposure window is deterministic and directly proportional to the configured interval. This is a design/config-dependent condition, not a remote unauthenticated exploit, but it is a real gap between the claimed per-request sync behavior (per the file's own doc comment) and the actual implementation.

### Recommendation
Either (a) update the doc comment to accurately reflect that sync is interval-based only and strongly recommend a short `UpstreamSyncInterval` for security-sensitive deployments, or (b) enforce revalidation against the upstream LDAP server (or at least re-check an "active"/membership flag) synchronously on privileged actions (e.g., before honoring `RequiresAdminRole`), or (c) shrink the trust window by triggering an on-demand incremental check for the specific user in `AuthorizedUserWithSession`/`FindUserByAPIToken` rather than relying solely on the periodic full-directory sync.

### Proof of Concept
1. Configure the node with `LDAPAuth` and a non-zero `UpstreamSyncInterval` (e.g., 5 minutes).
2. An LDAP user in the Admin group logs in via `CreateSession`, caching `role=admin` in `ldap_sessions`.
3. An operator removes the user from the Admin LDAP group (or deactivates/deletes the account) in the upstream directory.
4. Within the sync interval window, the user's existing session cookie still authenticates as `admin` via `AuthorizedUserWithSession` (`core/sessions/ldapauth/ldap.go:345-373`), since role/validity is read only from the local `ldap_sessions` cache, and admin-only endpoints (e.g., `POST /v2/users`) remain accessible until `LDAPServerStateSyncer.Work` next runs and purges/updates the cached row.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L1-23)
```go
/*
The LDAP authentication package forwards the credentials in the user session request
for authentication with a configured upstream LDAP server

This package relies on the two following local database tables:

	ldap_sessions: 	Upon successful LDAP response, creates a keyed local copy of the user email
	ldap_user_api_tokens: User created API tokens, tied to the node, storing user email.

Note: user can have only one API token at a time, and token expiration is enforced

User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function

This implementation is read only; user mutation actions such as Delete are not supported.

MFA is supported via the remote LDAP server implementation. Sufficient request time out should accommodate
for a blocking auth call while the user responds to a potential push notification callback.
*/
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

**File:** core/sessions/ldapauth/sync.go (L189-275)
```go
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
```
